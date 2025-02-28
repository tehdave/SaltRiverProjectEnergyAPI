"""Provides a client for interacting with the Salt River Project (SRP) API.

The SaltRiverProjectClient class allows users to authenticate with their SRP account
and retrieve various data such as hourly energy usage, daily weather information, and
user outage information.
Classes:
    SaltRiverProjectClient: A client for interacting with the SRP API.
Exceptions:
    ValueError: Raised when invalid arguments are provided to the SaltRiverProjectClient
                constructor.
Functions:
    __init__(self, billing_account, username, password):
    authorise_login(self):
    is_authorised(self) -> bool:
    get_hourly_usage(self, start_date, end_date) -> List[HourlyUsage]:
    get_daily_weather(self) -> List[WeatherData]:
    get_user_outage(self) -> SelfOutageData:
"""

import datetime
from typing import List
from urllib.parse import unquote

import requests

from . import logging
from .const import (
    API_HOURLY_USAGE_URI,
    API_LOGIN_URI,
    API_RATE_METADATA_URI,
    API_USER_OUTAGE_URI,
    API_WEATHER_DATA_URI,
    API_XSRF_URI,
    BASE_API_URL,
    BILLING_ACCOUNT_LENGTH,
)
from .exceptions import (
    InvalidBillingAccountError,
    InvalidPasswordError,
    InvalidUsernameError,
)
from .objects import (
    CostData,
    EnergyUsageData,
    HourlyUsage,
    KwhData,
    RateMetaData,
    SelfOutageData,
    WeatherData,
)


class SaltRiverProjectClient:
    """The SaltriverProjectClient class.

    This client allows users to authenticate with their SRP account and retrieve various
    data such as hourly energy usage and daily weather information.

    Attributes:
        billingAccount (str): The 9 digit SRP Billing Account.
        username (str): The username used to login. Usually your email address.
        password (str): The password used to login.
        apiSession (requests.Session): The session used for making API requests.
        xsrf_token (str): The XSRF token retrieved after successful login
            and authorisation.

    Methods:
        __init__(billingAccount, username, password):
            raise InvalidUsernameError()
        authoriseLogin():
            raise InvalidPasswordError()
        getHourlyUsage(startDate, endDate) -> List[HourlyUsage]:
            Fetches hourly usage data for the specified date range.
        getDailyWeather() -> List[WeatherData]:
            raise InvalidBillingAccountError()

    """

    def __init__(self, billing_account, username, password):
        """Initialize the client with billing account, username, and password.

        Args:
            billing_account (str): The billing account number.
            Must be a 9-character string.
            username (str): The username for the account.
            password (str): The password for the account.

        Raises:
            InvalidBillingAccountError: If the billing account is not a string
            or not 9 characters long.
            InvalidUsernameError: If the username is not a string or is empty.
            InvalidPasswordError: If the password is not a string or is empty.

        """
        self.logger = logging.getLogger(__name__)

        if not isinstance(billing_account, str) or not billing_account:
            raise InvalidBillingAccountError
        if len(billing_account) != BILLING_ACCOUNT_LENGTH:
            raise InvalidBillingAccountError
        if not isinstance(username, str) or not username:
            raise InvalidUsernameError
        if not isinstance(password, str) or not password:
            raise InvalidPasswordError

        self.billing_account = billing_account
        self.username = username
        self.password = password
        self.xsrf_token = None
        self.api_session = requests.Session()

    def authorise_login(self):
        """Authorises the login credentials and retrieves the XSRF token.

        Returns:
        bool: True if authorisation is successful, False otherwise.

        """
        self.logger.debug("Authorising login.")
        try:
            authenticate_request = self.api_session.post(
                BASE_API_URL + API_LOGIN_URI,
                data={"username": self.username, "password": self.password},
            )
            response_data = authenticate_request.json()
            # If the response contains a successful message:
            is_authenticated = response_data["message"] == "Log in successful."
            if is_authenticated:
                self.logger.debug("Login successful. Attempting to authorise.")
                authorise_request = self.api_session.get(BASE_API_URL + API_XSRF_URI)
                response_data = authorise_request.json()
                is_authorised = response_data["message"] == "Success"
                if is_authorised:
                    self.logger.debug("Authorisation successful.")
                    self.xsrf_token = unquote(response_data["xsrfToken"])
                    return True
                self.logger.debug("Authorisation failed.")
                return False
            self.logger.debug("Login failed.")
            return False  # noqa: TRY300

        except requests.RequestException:
            self.logger.exception("Exception occurred")
            return False

    def is_authorised(self) -> bool:
        """Check if the client is authorised to make API requests.

        Returns:
            bool: True if the client is authorised, False otherwise.

        """
        # Check to see if we have an XSRF token
        self.logger.debug("Checking if client is authorised.")
        if hasattr(self, "xsrf_token"):
            self.logger.debug("Client has a token.")
            # We have a token. See if it's valid.  We will do this by
            # making a simple API call
            # and seeing if we get a 200 response.
            auth_request = self.api_session.get(
                BASE_API_URL
                + API_USER_OUTAGE_URI.format(billingAccount=self.billing_account),
                headers={"x-xsrf-token": self.xsrf_token},
            )
            if auth_request.ok:
                # We are authorised
                return True
            self.logger.debug("Client is not authorised.")
            # We are not authorised. Attempt to Authenticate and Authorise.
            return self.authorise_login()
        self.logger.debug("Client does not have a token.")
        # We don't have a token. Attempt to Authenticate and Authorise.
        return self.authorise_login()

    def get_hourly_usage(self, start_date, end_date) -> EnergyUsageData:
        """Retrieve hourly energy usage data for a given date range.

        Args:
            start_date (str): The start date in the format "dd-mm-yyyy".
            end_date (str): The end date in the format "dd-mm-yyyy".

        Returns:
            List[HourlyUsage]: A list of HourlyUsage objects containing energy usage
            data for each hour within the specified date range.

        Raises:
            ValueError: If the date format is incorrect or if the API response is
            invalid.

        """
        # Convert datetime to strings
        str_startdate = datetime.datetime.strptime(start_date, "%d-%m-%Y")
        str_enddate = datetime.datetime.strptime(end_date, "%d-%m-%Y")

        # We can only make API requests if we are authorised
        if not self.is_authorised():
            self.logger.debug("Client is not authorised.")
            return False

        response = self.api_session.get(
            BASE_API_URL
            + API_HOURLY_USAGE_URI.format(
                billingAccount=self.billing_account,
                startDate=str_startdate,
                endDate=str_enddate,
            ),
            headers={"x-xsrf-token": self.xsrf_token},
        )

        api_response = response.json()
        daily_energy_usage = EnergyUsageData(energy_usage=[])

        for item in api_response["hourlyUsageList"]:
            kwh_data: KwhData = KwhData(
                on_peak_kwh = item["onPeakKwh"],
                off_peak_kwh = item["offPeakKwh"],
                shoulder_kwh = item["shoulderKwh"],
                super_off_peak_kwh = item["superOffPeakKwh"],
                total_kwh = item["totalKwh"],
            )

            cost_data: CostData = CostData(
                on_peak_cost=item["onPeakCost"],
                off_peak_cost=item["offPeakCost"],
                shoulder_cost=item["shoulderCost"],
                super_off_peak_cost=item["superOffPeakCost"],
                total_cost=item["totalCost"],
            )

            # Some smoke and mirrors here to turn the returned string into a datetime
            # object and parse out the date and time into separate properties.
            iso_date_from_data = datetime.datetime.fromisoformat(item["date"])
            data_date = iso_date_from_data.date()
            data_time = iso_date_from_data.time()
            hourly_usage: HourlyUsage = HourlyUsage(
                date=data_date,
                hour=data_time,
                kwh_data=kwh_data,
                cost_data=cost_data,
            )

            daily_energy_usage.energy_usage.append(hourly_usage)
        return daily_energy_usage

    def get_daily_weather(self) -> List[WeatherData]:
        """Fetch daily weather data from the API.

        This method sends a GET request to the weather data endpoint of the API
        and retrieves the daily weather data. The data is then parsed and
        converted into a list of WeatherData objects.

        Returns:
            List[WeatherData]: A list of WeatherData objects containing the
            weather information for each day.

        Raises:
            Exception: If there is an error during the API request or data
            parsing, an exception is caught and its representation is printed.

        """
        # We can only make API requests if we are authorised
        if not self.is_authorised():
            self.logger.debug("Client is not authorised.")
            return False

        try:
            weather_request = self.api_session.get(
                BASE_API_URL + API_WEATHER_DATA_URI,
                headers={"x-xsrf-token": self.xsrf_token},
            )
            api_response = weather_request.json()
            weather_data_collection = []
            for item in api_response:
                weather_data = WeatherData(
                    item["weatherDate"], item["high"], item["low"], item["average"]
                )
                weather_data_collection.append(weather_data)
            return weather_data_collection  # noqa: TRY300

        except requests.RequestException:
            self.logger.exception("Exception occurred")
            return False

    def get_user_outage(self) -> SelfOutageData:
        """Fetch the user's outage information from the API.

        This method sends a GET request to the API endpoint to retrieve the
        user's outage data. It constructs the request URL using the base API
        URL and the user's billing account. The response is expected to be in
        JSON format and contains information about the outage.

        Returns:
            SelfOutageData: An instance of SelfOutageData containing the
            outage information.

        Raises:
            Exception: If there is an error during the API request or response
            parsing, an exception is caught and printed.

        """
        # We can only make API requests if we are authorised
        if not self.is_authorised():
            self.logger.debug("Client is not authorised.")
            return None

        try:
            self_outage_request = self.api_session.get(
                BASE_API_URL
                + API_USER_OUTAGE_URI.format(billingAccount=self.billing_account),
                headers={"x-xsrf-token": self.xsrf_token},
            )
            api_response = self_outage_request.json()
            return SelfOutageData(
                api_response["isInOutageArea"],
                api_response["estimatedRestorationTime"],
                api_response["reportedOutageTime"],
                api_response["estimatedUsersImpacted"],
            )

        except requests.RequestException:
            self.logger.exception("RequestException occurred")
            return None

    def get_rate_metadata(self) -> RateMetaData:
        """Retrieve the rate metadata from the API.

        Returns:
            RateMetaData: The rate metadata if the client is authorised, otherwise None.

        """
        # We can only make API requests if we are authorised
        if not self.is_authorised():
            self.logger.debug("Client is not authorised.")
            return None
        try:
            rate_metadata_request = self.api_session.get(
                BASE_API_URL
                + API_RATE_METADATA_URI.format(billingAccount=self.billing_account),
                headers={"x-xsrf-token": self.xsrf_token},
            )
            api_response = rate_metadata_request.json()
            return RateMetaData(
                api_response["description"],
                api_response["short_description"],
                api_response["price_plan_url"],
                api_response["is_demand"],
                api_response["is_metered"],
                api_response["is_solar"]
            )

        except requests.RequestException:
            self.logger.exception("RequestException occurred")
            return None
