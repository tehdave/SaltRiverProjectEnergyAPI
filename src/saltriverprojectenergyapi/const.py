BASE_API_URL = "https://myaccount.srpnet.com/myaccountapi/api/"

API_LOGIN_URI = "login/authorize"
API_XSRF_URI = "login/antiforgerytoken"

API_RATE_METADATA_URI   = "accounts/getratemetadata?billdccount={billingAccount}"
API_HOURLY_USAGE_URI    = "usage/hourlydetail?billaccount={billingAccount}&beginDate={startDate}&endDate={endDate}"
API_WEATHER_DATA_URI    = "usage/dailyweather"
API_USER_OUTAGE_URI     = "outages/userinoutage?billdccount={billingAccount}"