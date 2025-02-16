"""Client Module

This module contains the main class used to interact with the Salt River Project
Data API.
"""

import datetime
import requests
from typing import List
from urllib.parse import unquote
from .objects import (
    HourlyUsage,
    WeatherData,
    SelfOutageData,
)
from .const import (
    BASE_API_URL,
    API_LOGIN_URI,
    API_XSRF_URI,
    API_HOURLY_USAGE_URI,
    API_WEATHER_DATA_URI,
    API_USER_OUTAGE_URI
)

class SaltRiverProjectClient:
    """SaltRiverProjectClient is a client for interacting with the Salt River Project (SRP) API.
    This client allows users to authenticate with their SRP account and retrieve various data such as hourly energy usage and daily weather information.
    Attributes:
        billingAccount (str): The 9 digit SRP Billing Account.
        username (str): The username used to login. Usually your email address.
        password (str): The password used to login.
        apiSession (requests.Session): The session used for making API requests.
        xsrf_token (str): The XSRF token retrieved after successful login and authorisation.
    Methods:
        __init__(billingAccount, username, password):
            Initializes the SaltRiverProjectClient with the provided credentials.
        authoriseLogin():
            Authorises the login credentials and retrieves the XSRF token.
        getHourlyUsage(startDate, endDate) -> List[HourlyUsage]:
            Fetches hourly usage data for the specified date range.
        getDailyWeather() -> List[WeatherData]:
            Fetches daily weather data.
    """

    def __init__(self, billingAccount, username, password):
        """
        Initializes the client with the given billing account, username, and password.
        Args:
            billingAccount (str): A 9 digit string representing the billing account.
            username (str): A non-empty string representing the username.
            password (str): A non-empty string representing the password.
        Raises:
            ValueError: If billingAccount is not a 9 digit string.
            ValueError: If username is not a non-empty string.
            ValueError: If password is not a non-empty string.
        """

        if not isinstance(billingAccount, str) or len(billingAccount) != 9:
            raise ValueError("billingAccount must be a 9 digit string.")
        if not isinstance(username, str) or not username:
            raise ValueError("username must be a non-empty string.")
        if not isinstance(password, str) or not password:
            raise ValueError("password must be a non-empty string.")
        
        self.billingAccount = billingAccount
        self.username = username
        self.password = password
        self.apiSession = requests.Session()

    def authoriseLogin(self):
        """Authorises the login credentials and retrieves the XSRF token.

        Returns:
        bool: True if authorisation is successful, False otherwise.
        """

        try:
            authenticateRequest = self.apiSession.post(
                BASE_API_URL
                + API_LOGIN_URI,
                data={"username": self.username, "password": self.password}
            )
            responseData = authenticateRequest.json()
            # If the response contains a successful message:
            isAuthenticated = responseData['message'] == "Log in successful."
            print("Login was successful. Attempting to Authorise.")
            if isAuthenticated:
                authoriseRequest = self.apiSession.get(
                    BASE_API_URL
                    + API_XSRF_URI
                )
                responseData = authoriseRequest.json()
                isAuthorised = responseData['message'] == "Success"
                if isAuthorised:
                    self.xsrf_token = unquote(responseData["xsrfToken"])
                    return True
                # End if isAuthorised
            # End if isAuthenticated
            return False

            
        except Exception as e:
            print("Exception:", repr(e))
            return False
                
    def isAuthorised(self) -> bool:
        """
        Checks if the client is authorised to make API requests.
        Returns:
            bool: True if the client is authorised, False otherwise.
        """

        # Check to see if we have an XSRF token
        print("Checking if client is authorised.")
        if hasattr(self, "xsrf_token"):
            print("Client has a token.")
            # We have a token. See if it's valid.  We will do this by making a simple API call
            # and seeing if we get a 200 response.
            authRequest = self.apiSession.get(
                BASE_API_URL
                + API_USER_OUTAGE_URI.format(billingAccount=self.billingAccount),
                headers = {"x-xsrf-token": self.xsrf_token}
            )
            if authRequest.status_code == 200:
                # We are authorised
                return True
            else:
                print("Client is not authorised.")
                # We are not authorised. Attempt to Authenticate and Authorise.
                return self.authoriseLogin()
        else:
            print("Client does not have a token.")
            # We don't have a token. Attempt to Authenticate and Authorise.
            return self.authoriseLogin()

    def getHourlyUsage(self, startDate, endDate) -> List[HourlyUsage]:
        """
        Retrieves hourly energy usage data for a given date range.
        Args:
            startDate (str): The start date in the format "dd-mm-yyyy".
            endDate (str): The end date in the format "dd-mm-yyyy".
        Returns:
            List[HourlyUsage]: A list of HourlyUsage objects containing energy usage data for each hour within the specified date range.
        Raises:
            ValueError: If the date format is incorrect or if the API response is invalid.
        """

        # Convert datetime to strings
        str_startdate = datetime.datetime.strptime(startDate, "%d-%m-%Y")
        str_enddate = datetime.datetime.strptime(endDate, "%d-%m-%Y")

        # We can only make API requests if we are authorised
        if self.isAuthorised() == False:
            print("Client is not authorised.")
            return False
        
        response = self.apiSession.get(
            BASE_API_URL
            + API_HOURLY_USAGE_URI.format(billingAccount=self.billingAccount, startDate=str_startdate, endDate=str_enddate),
            headers = {"x-xsrf-token": self.xsrf_token}
        )

        apiResponse = response.json()
        energy_data_collection = []
        for item in apiResponse['hourlyUsageList']:
            energy_data = HourlyUsage(
                item['date'],
                item['hour'],
                item['onPeakKwh'],
                item['offPeakKwh'],
                item['shoulderKwh'],
                item['superOffPeakKwh'],
                item['totalKwh'],
                item['onPeakCost'],
                item['offPeakCost'], 
                item['shoulderCost'],
                item['superOffPeakCost'],
                item['totalCost']
            )
            energy_data_collection.append(energy_data)
            
        return energy_data_collection

    def getDailyWeather(self) -> List[WeatherData]:
        """
        Fetches daily weather data from the API.
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
        if self.isAuthorised() == False:
            print("Client is not authorised.")
            return False
        
        try:
            weatherRequest = self.apiSession.get(
                BASE_API_URL
                + API_WEATHER_DATA_URI,
                headers = {"x-xsrf-token": self.xsrf_token}
            )
            apiResponse = weatherRequest.json()
            weather_data_collection = []
            for item in apiResponse:
                weather_data = WeatherData(
                    item['weatherDate'],
                    item['high'],
                    item['low'],
                    item['average']
                )
                weather_data_collection.append(weather_data)
            return weather_data_collection
        
        except Exception as e:
            print("Exception:", repr(e))
            return False
        
    def getUserOutage(self) -> SelfOutageData:
        """
        Fetches the user's outage information from the API.
        This method sends a GET request to the API endpoint to retrieve the user's outage data.
        It constructs the request URL using the base API URL and the user's billing account.
        The response is expected to be in JSON format and contains information about the outage.
        Returns:
            SelfOutageData: An instance of SelfOutageData containing the outage information.
        Raises:
            Exception: If there is an error during the API request or response parsing, an exception is caught and printed.
        """
        # We can only make API requests if we are authorised
        if self.isAuthorised() == False:
            print("Client is not authorised.")
            return False
        
        try:
            selfOutageRequest = self.apiSession.get(
                BASE_API_URL
                + API_USER_OUTAGE_URI.format(billingAccount=self.billingAccount),
                headers = {"x-xsrf-token": self.xsrf_token} 
            )
            apiResponse = selfOutageRequest.json()
            self_outage_data = SelfOutageData(
                apiResponse['isInOutageArea'],
                apiResponse['estimatedRestorationTime'],
                apiResponse['reportedOutageTime'],
                apiResponse['estimatedUsersImpacted']
            )
            return self_outage_data
        
        except Exception as e:
            print("Exception:", repr(e))
