# WeatherAPI
Gets current weather data and forecast for a city

## Dependencies:
* Flask
```
pip install flask
```

* cachetools
```
pip install cachetools 
```

* Python 3

This is a python3 application!

## Environment variables:

* WAPI_API_KEY: (required)

A valid OpenWeather appid token

* WAPI_PORT:

The port on which to run the application. Defaulted to 8081.

* WAPI_TEMPERATURE_CONFIG:

Choose the metric for temperature.
Both Celsius and Fahrenheit = 0
Fahrenheit = 1
Celsius = 2

Defaulted to 0.

## How to run:
On project root directory:
```
export WAPI_API_KEY=$KEY
python3 main.py
```