"""Client Module

This module contains the main class used to interact with the Salt River Project
Data API.
"""

import datetime
import requests
from urllib.parse import unquote
from saltriverprojectclient.objects.hourly_usage import HourlyUsage
from saltriverprojectclient.objects.weather_data import WeatherData
from typing import List
from .const import (
    BASE_API_URL,
    API_LOGIN_URI,
    API_XSRF_URI,
    API_HOURLY_USAGE_URI,
    API_WEATHER_DATA_URI
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
        """Initializes the SaltRiverProjectClient with the provided credentials.

        Parameters:
        billingAccount: string
            The 9 digit SRP Billing Account.
        username: string
            The username used to login. Usually your email address.
        password: string
            The password used to login.
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
                
    def getHourlyUsage(self, startDate, endDate) -> List[HourlyUsage]:
        """Fetches hourly usage data for the specified date range.

        Parameters:
        startDate: datetime
            The start date for the data retrieval.
        endDate: datetime
            The end date for the data retrieval.

        Returns:
        List[HourlyUsage]: A list of HourlyUsage objects containing per hour usage information.
        """
        # Convert datetime to strings
        str_startdate = datetime.datetime.strptime(startDate, "%d-%m-%Y")
        str_enddate = datetime.datetime.strptime(endDate, "%d-%m-%Y")

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
        """Fetches daily weather data.

        Returns:
        List[WeatherData]: A list of WeatherData objects containing daily weather information.
        """
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
