# Salt River Project Client

This module provides a Python client for interacting with the Salt River Project (SRP) energy API. It allows users to retrieve energy usage data, billing information, and other related data from SRP.

## Usage

Here is an example of how to use the Salt River Project Client:

```python
from saltriverprojectenergyapi.client import SaltRiverProjectClient

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
hourly_usage_data = client.getHourlyUsage(startDate='01-01-2025', endDate='01-05-2025')
# hourly_usage_data is a List[HourlyUsage] * See objects/hourly_usage.py


# Weather data does not take any parameters, and just returns a full weather dataset.
weatherData = client.getDailyWeather()
# weatherData is a List[WeatherData] * See objects/weather_data.py
```

## Currently supported methods

Currently, this client api supports two methods.
1. getHourlyUsage
1. getDailyWeather

```python
# The getHourlyUsage method takes 2 parameters:
#   startDate: a string formatted as dd-mm-yyyy e.g.: '01-01-2025' for 1 Jan 2025
#   endDate: a string formatted as dd-mm-yyyy e.g.: '31-01-2025' for 31 Jan 2025
# The return type from the getHourlyUsage is a List[] of HourlyUsage objects.

# The getDailyWeather method takes no parameters:
# The return type from the getDailyWeather is a List[] of WeatherData objects.
```

## Features

- Retrieve energy usage data for a specified date range
- Retrieve weather data associated with your account
