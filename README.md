# Salt River Project Client

This module provides a Python client for interacting with the Salt River Project (SRP) energy API. It allows users to retrieve energy usage data, billing information, and other related data from SRP.

## Usage

Here is an example of how to use the Salt River Project Client:

```python
from saltriverprojectenergyapi import SaltRiverProjectClient

# Initialize the client with your Billing Account and login info
client = SaltRiverProjectClient(
    billingAccount="Billing Account Number",
    username="SRP email_address or login name",
    password="SRP password"
)

# Authenticate and Authorize the client.
# This is a boolean return value, so you can verify if the authentication
# and authorisation were successful or not.
isAuthorised = client.authoriseLogin()

# Retrieve energy usage data
# The dates are passed in as string values with the format dd-mm-yyyy
myHourlyUsageData = client.getHourlyUsage(startDate='01-01-2025', endDate='01-05-2025')
# myHourlyUsageData is a List[HourlyUsage] * See objects/hourly_usage.py

# Weather data does not take any parameters, and just returns a full weather dataset.
myWeatherData = client.getDailyWeather()
# myWeatherData is a List[WeatherData] * See objects/weather_data.py

# Retrieve outage data for your billing account.
# The Outage Data endpoint does not take any parameters, and returns a SelfOutageData object.
myOutageData = client.getUserOutage()
if(myOutageData.isInOutageArea):
    print("User is in an outage area.)
```

## Currently supported methods

Currently, this client api supports the following methods.
1. getHourlyUsage
1. getDailyWeather
1. getUserOutage

## Features

- Retrieve energy usage data for a specified date range
- Retrieve weather data associated with your account
