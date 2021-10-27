import requests
import json
from .logger import log, WARNING as LOG_WARNING, OK as LOG_OK, ERROR as LOG_ERROR
from .parser import OpenWeatherParser
from datetime import datetime
from cachetools import TTLCache
import os
import sys
import unittest

EXTERNAL_API_BASE_URL = "https://api.openweathermap.org/data/2.5"

WEATHER_EXTERNAL_ENDPOINT = "weather"
FORECAST_EXTERNAL_ENDPOINT = "forecast"

CACHE_STORAGE_TIME_SECONDS = 120
CACHE_MAXSIZE = 100

# class responsible for fetching weather data from external api or cache
# also responsible for updating the cache after external api requests
# Attributes
#   url: base url of external API
#   api_key: token necessary for accessing external API
#   parser: object responsible for parsing external API responses
#   cache: data structure used for saving external API data in order to avoid unnecessarily making the same request more than once
#       the cache functions as a python dictionary that uses string tuples of size 2 as keys. 
#       the first element of each tuple key is the city in lowercase, the second element is the country code.
#       the values of the dictionary are JSON strings with the weather data ready to be sent as response
#       each value of the dictionary expires after {CACHE_STORAGE_TIME_SECONDS} seconds after insertion
#       E.g of cache data structure:
#       {
#           ("Montevideo", "uy"): "{
#               "location_name": "Montevideo, UY",
#               "temperature": "88 °F, 31 °C",
#               "pressure": "1020 hpa",
#               "cloudiness": "Clear sky",
#               "humidity": "29%",
#               "sunrise": "05:47",
#               "sunset": "19:09",
#               "geo_coordinates": "[-34.83, -56.17]",
#               "requested_time": "27-10-2021 13:55:23",
#               "forecast": [...]
#           }",
#           ("Buenos Aires", "ar"): "{ ... }",
#           ("Santiago", "cl"): "{ ... }"   
#       }
class WeatherClient:

    # PUBLIC METHODS

    def __init__(self):

        self.url = EXTERNAL_API_BASE_URL

        self.api_key = os.environ.get('WAPI_API_KEY')
        if self.api_key is None:
            log(LOG_ERROR, "Application initialized without an api key. Please set the WAPI_API_KEY environment to a valid OpenWeather appid")
            sys.exit()

        temp_config = os.environ.get('WAPI_TEMPERATURE_CONFIG')
        if temp_config is None:
            self.parser = OpenWeatherParser()
        else:
            try:
                self.parser = OpenWeatherParser(int(temp_config))
            except ValueError as e:
                log(LOG_WARNING, "WAPI_TEMPERATURE_CONFIG environment variable was set to an invalid value. Initializing with default value...")
                self.parser = OpenWeatherParser()
            except Exception as e:
                # should be unreachable
                log(LOG_WARNING, "Couldn't set temp config to provided env var because of raised exception: \n{}. \nInitializing with default value..."
                    .format(repr(e)))
                self.parser = OpenWeatherParser()

        self.cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_STORAGE_TIME_SECONDS)
    
    # gets weather and forecast for a location defined by a country code and a city name.
    # validates the country and city parameters to be of the expected format
    
    # Parameters
    #   country: string expected to be of size 2 and lowercase. E.g "co" 
    #   city: string. E.g "Bogota" 

    # Output
    #     dictionanary with weather data
    #     {
    #        "weather_field_1": "..."
    #        .
    #        .
    #        .
    #        "weather_field_n": "..."
    #        "forecast": {...}
    #     }
    def get_weather(self, country, city):

        # validating parameters...
        errors = []
        city_errors = WeatherClient.validate_city(city)
        country_errors = WeatherClient.validate_country(country)
        errors.extend(city_errors)
        errors.extend(country_errors)
        if len(errors) > 0:
            raise InvalidParameters(errors)

        city_country = (city.lower(), country)
        # checking cache...
        if city_country in self.cache:

            log(LOG_OK, "Weather data for {}, {} was found on cache, retrieving...".format(city, country))
            return self.cache[city_country]

        else: 
            
            # running get weather logic... (external api)
            requested_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            result = {
                "location_name": "{}, {}".format(city.capitalize(), country.upper())
            }
            current = self.__get_current_weather(country, city)
            forecast = self.__get_forecast(country, city)

            # putting stuff together...
            result.update(current)
            result['requested_time'] = requested_time
            result['forecast'] = forecast
            weather_json = json.dumps(result)

            # store in cache...
            self.cache[city_country] = weather_json

            return weather_json

    # PRIVATE METHODS

    # uses an external api to get current weather for a location, returns dictionary
    # and parses the response to the desired format using the parser injected at initialization
    # Parameters
    #   country_code: size 2 string, lowercase. E.g "co" 
    #   city: string. E.g "Bogota" 
    # Output 
    #   weather dictionary from an OpenWeather OK Response
    def __get_current_weather(self, country_code, city):

        # making request to external api...
        params = {
            "q": "{},{}".format(city, country_code),
            "appid": self.api_key 
        }
        log(LOG_OK, "Making current weather request to external API for {}, {}".format(city, country_code))
        unparsed_result = self.__make_request(params, WEATHER_EXTERNAL_ENDPOINT)

        # parsing response...
        result = self.parser.parse_weather(unparsed_result)

        return result


    # uses an external api to get forecast for a location
    # and parses the response to the desired format using the parser injected at initialization
    # Parameters
    #   country_code: size 2 string, lowercase. E.g "co" 
    #   city: string. E.g "Bogota" 
    # Output 
    #   forecast dictionary from an OpenWeather OK Response
    def __get_forecast(self, country_code, city):

        # making request to external api...
        params = {
            "q": "{},{}".format(city, country_code),
            "appid": self.api_key 
        }
        log(LOG_OK, "Making forecast request to external API for {}, {}".format(city, country_code))
        unparsed_result = self.__make_request(params, FORECAST_EXTERNAL_ENDPOINT)

        # parsing response...
        result = self.parser.parse_forecast(unparsed_result)

        return result

    # makes the actual request to the OpenWeather API and handles response
    # Parameters
    #   endpoint: A string. Should take the value of either WEATHER_EXTERNAL_ENDPOINT or FORECAST_EXTERNAL_ENDPOINT
    def __make_request(self, params, endpoint):
        # validation...
        if endpoint not in (WEATHER_EXTERNAL_ENDPOINT, FORECAST_EXTERNAL_ENDPOINT):
            raise ValueError("trying to make a request to unsupported OpenWeather endpoint '{}'".format(endpoint))

        # make request...
        url = "{}/{}".format(self.url, endpoint)
        response = requests.get(url, params)

        # handling response...
        code = response.status_code
        if code == 200:
            return json.loads(response.content)
        else:
            if code == 401:
                raise InvalidAPIKey
            if code == 404:
                raise CityNotFound


    # The validate methods could/should be private but I didn't find a way to apply unittests to private methods in python
    def validate_city(city):
        errors = []
        if city is None:
            errors.append("missing city parameter")
        else: 
            if not isinstance(city, str):
                errors.append("invalid city: cannot be parsed as a string")
            if not all(char.isalpha() or char.isspace() for char in city):
                errors.append("invalid city: contains non-alphabetical, non-space values")
        return errors

    def validate_country(country):
        errors = []
        if country is None:
            errors.append("missing country parameter")
        else: 
            if not isinstance(country, str):
                errors.append("invalid country: cannot be parsed as a string")
            if len(country) > 2:
                errors.append("invalid country: larger than two")
            if len(country) < 2:
                errors.append("invalid country: shorter than two")
            if not country.islower():
                errors.append("invalid country: not an alphabetical lowercase value")
            if not country.isalpha():
                errors.append("invalid country: contains non-alphabetical values")
        return errors

# EXCEPTIONS
# custom exceptions raised by this module

class InvalidParameters(Exception):
    def __init__(self, errors):
        self.errors = errors 

class InvalidAPIKey(Exception):
    def __init__(self):
        pass

class CityNotFound(Exception):
    def __init__(self):
        pass

# UNITTESTS

class TestValidators(unittest.TestCase):
    def test_valid_city_common(self):
        input = "Montevideo"
        expected_output = []
        self.assertEqual(WeatherClient.validate_city(input), expected_output)

    def test_valid_city_with_spaces(self):
        input = "Los Angeles"
        expected_output = []
        self.assertEqual(WeatherClient.validate_city(input), expected_output)

    def test_valid_city_weird(self):
        input = "lAs vEgaS"
        expected_output = []
        self.assertEqual(WeatherClient.validate_city(input), expected_output)

    def test_invalid_city_numbers(self):
        input = "12345"
        expected_output = ['invalid city: contains non-alphabetical, non-space values']
        self.assertEqual(WeatherClient.validate_city(input), expected_output)

    def test_invalid_city_alphanumeric(self):
        input = "1New York"
        expected_output = ['invalid city: contains non-alphabetical, non-space values']
        self.assertEqual(WeatherClient.validate_city(input), expected_output)

    def test_invalid_city_symbols(self):
        input = "Madrid %"
        expected_output = ['invalid city: contains non-alphabetical, non-space values']
        self.assertEqual(WeatherClient.validate_city(input), expected_output)

    def test_valid_country(self):
        input = "ar"
        expected_output = []
        self.assertEqual(WeatherClient.validate_country(input), expected_output)

    def test_invalid_country_uppercase(self):
        input = "AR"
        expected_output = ['invalid country: not an alphabetical lowercase value']
        self.assertEqual(WeatherClient.validate_country(input), expected_output)

    def test_invalid_country_too_long(self):
        input = "arg"
        expected_output = ['invalid country: larger than two']
        self.assertEqual(WeatherClient.validate_country(input), expected_output)

    def test_invalid_country_too_short(self):
        input = "a"
        expected_output = ['invalid country: shorter than two']
        self.assertEqual(WeatherClient.validate_country(input), expected_output)

    def test_invalid_country_too_long_and_uppercase(self):
        input = "ARG"
        expected_output = ['invalid country: larger than two', 'invalid country: not an alphabetical lowercase value']
        self.assertEqual(WeatherClient.validate_country(input), expected_output)

    def test_invalid_country_too_short_and_uppercase(self):
        input = "A"
        expected_output = ['invalid country: shorter than two', 'invalid country: not an alphabetical lowercase value']
        self.assertEqual(WeatherClient.validate_country(input), expected_output)

    def test_invalid_country_numbers(self):
        input = "a1"
        expected_output = ['invalid country: contains non-alphabetical values']
        self.assertEqual(WeatherClient.validate_country(input), expected_output)

    def test_invalid_country_symbols(self):
        input = "a%"
        expected_output = ['invalid country: contains non-alphabetical values']
        self.assertEqual(WeatherClient.validate_country(input), expected_output)
