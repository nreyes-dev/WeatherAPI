from .logger import log, WARNING as LOG_WARNING
from datetime import datetime 
import unittest

# temp configurations
FAHRENHEIT_AND_CELSIUS = 0
FAHRENHEIT = 1
CELSIUS = 2

TEMP_CONFIGURATIONS = (CELSIUS, FAHRENHEIT, FAHRENHEIT_AND_CELSIUS)

# Class responsible for translating the responses of the Open Weather external API into the format that meets this API's requirements
class OpenWeatherParser:

    def __init__(self, temp_config=0):
        if temp_config not in TEMP_CONFIGURATIONS:
            raise ValueError("trying to initialize parser with invalid temp config '{}'".format(temp_config))
        self.temp_config = temp_config

    # Parses weather response data from a call to the Open Weather external API into a human-readable dictionary 
    # Parameters:
    #   weather: Dictionary with Opean Weather's OK response content for weather
    #   is_forecast_item: Indicitates if the passed-in "weather" parameter is a forecast item or not (as there's some slight differences, e.g. forecast items
    #       don't have sunrise/sunset)
    # Output:
    #   Human-readable dictionary with weather information
    def parse_weather(self, weather, is_forecast_item = False):
        if not isinstance(weather, dict):
            raise TypeError("trying to parse weather that isn't a dictionary")
        result = {}
        self.__parse_temperature(self.temp_config, weather, result)
        self.__parse_pressure(weather, result)
        self.__parse_cloudiness(weather, result)
        self.__parse_humidity(weather, result)
        if not is_forecast_item:
            self.__parse_sunrise(weather, result)
            self.__parse_sunset(weather, result)
            self.__parse_geocoordinates(weather, result)
        return result
    
    # Parses forecast response data from a call to the Open Weather's forecast external API into a human-readable dictionary 
    # Parameters:
    #   weather: Dictionary list with Opean Weather's OK response content for forecasts
    # Output:
    #   Human-readable dictionary list with forecast information
    def parse_forecast(self, forecast):
        if not isinstance(forecast, dict):
            raise TypeError("trying to parse forecast that isn't a dictionary")
        result = []

        # each item in the forecast's list is a weather dictionary just like the one from a /weather call but with a date
        for item in forecast['list']:
            if not isinstance(item, dict):
                raise TypeError("parsing a forecast list that has a non-dict item")

            # parsing weather data...
            partial_result = self.parse_weather(item, is_forecast_item=True)
            partial_result['datetime'] = item['dt_txt']

            result.append(partial_result)

        return result



    # PARSING FUNCTIONS:
    # the following are impure functions that build the passed-in result dictionary by adding a human-readable field parsed from the weather parameter

    def __parse_temperature(self, temp_config, weather, result):
        try:
            kelvin = weather['main']['temp']
            celsius = kelvin - 273.15

            if temp_config == CELSIUS:
                result['temperature'] = "{} °C".format(round(celsius))
            else:
                fahrenheit = kelvin*(9/5) - 459.67
                if temp_config == FAHRENHEIT:
                    result['temperature'] = "{} °F".format(round(fahrenheit))
                else: # FAHRENHEIT_AND_CELSIUS
                    result['temperature'] = "{} °F, {} °C".format(round(fahrenheit), round(celsius))
            
        except KeyError as e:
            log(LOG_WARNING, "key error when parsing temperature: {}".format(str(e)))

    def __parse_pressure(self, weather, result):
        try:
            pressure = weather['main']['pressure']
            result['pressure'] = "{} hpa".format(pressure)
        except KeyError as e:
            log(LOG_WARNING, "key error when parsing pressure: {}".format(str(e)))

    def __parse_cloudiness(self, weather, result):
        try:
            weather_list = weather['weather']
            # looking for cloudiness item...
            for item in weather_list:
                # if item is of tpye cloudiness... (id = 8xx)
                if item['id'] in range(800, 900):
                    result['cloudiness'] = item['description'].capitalize()
                    break

        except KeyError as e:
            log(LOG_WARNING, "key error when parsing cloudiness: {}".format(str(e)))
        except Exception as e:
            log(LOG_WARNING, "exception when parsing cloudiness: {}".format(str(e)))

    def __parse_humidity(self, weather, result):
        try:
            humidity = weather['main']['humidity']
            result['humidity'] = "{}%".format(humidity)
        except KeyError as e:
            log(LOG_WARNING, "key error when parsing humidity: {}".format(str(e)))

    def __parse_sunrise(self, weather, result):
        try:
            sunrise_unix = weather['sys']['sunrise']
            sunrise_datetime = datetime.fromtimestamp(sunrise_unix)
            result['sunrise'] = "{:02d}:{:02d}".format(sunrise_datetime.hour, sunrise_datetime.minute)
        except KeyError as e:
            log(LOG_WARNING, "key error when parsing sunrise: {}".format(str(e)))

    def __parse_sunset(self, weather, result):
        try:
            sunset_unix = weather['sys']['sunset']
            sunset_datetime = datetime.fromtimestamp(sunset_unix)
            result['sunset'] = "{:02d}:{:02d}".format(sunset_datetime.hour, sunset_datetime.minute)
        except KeyError as e:
            log(LOG_WARNING, "key error when parsing sunset: {}".format(str(e)))

    def __parse_geocoordinates(self, weather, result):
        try:
            lon = weather['coord']['lon']
            lat = weather['coord']['lat']
            result['geo_coordinates'] = "[{:.2f}, {:.2f}]".format(lat, lon)
        except KeyError as e:
            log(LOG_WARNING, "key error when parsing geocoordinates: {}".format(str(e)))


# UNITTESTS

class TestParser(unittest.TestCase):
    def test_parse_weather(self):
        input = {
            "coord": {
                "lon": -54.95,
                "lat": -34.9667
            },
            "weather": [
                {
                    "id": 800,
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01d"
                }
            ],
            "base": "stations",
            "main": {
                "temp": 302.21,
                "feels_like": 301.2,
                "temp_min": 302.21,
                "temp_max": 302.21,
                "pressure": 1020,
                "humidity": 32
            },
            "visibility": 10000,
            "wind": {
                "speed": 1.54,
                "deg": 180
            },
            "clouds": {
                "all": 0
            },
            "dt": 1635369297,
            "sys": {
                "type": 1,
                "id": 8712,
                "country": "UY",
                "sunrise": 1635324147,
                "sunset": 1635372277
            },
            "timezone": -10800,
            "id": 3440939,
            "name": "Punta del Este",
            "cod": 200
        }
        expected_output_celsius = {
            "temperature": "29 °C",
            "pressure": "1020 hpa",
            "cloudiness": "Clear sky",
            "humidity": "32%",
            "sunrise": "05:42",
            "sunset": "19:04",
            "geo_coordinates": "[-34.97, -54.95]",
        }

        expected_output_fahrenheit = {
            "temperature": "84 °F",
            "pressure": "1020 hpa",
            "cloudiness": "Clear sky",
            "humidity": "32%",
            "sunrise": "05:42",
            "sunset": "19:04",
            "geo_coordinates": "[-34.97, -54.95]",
        }

        expected_output_both = {
            "temperature": "84 °F, 29 °C",
            "pressure": "1020 hpa",
            "cloudiness": "Clear sky",
            "humidity": "32%",
            "sunrise": "05:42",
            "sunset": "19:04",
            "geo_coordinates": "[-34.97, -54.95]",
        }

        self.assertEqual(OpenWeatherParser(temp_config=CELSIUS).parse_weather(input), expected_output_celsius)
        self.assertEqual(OpenWeatherParser(temp_config=FAHRENHEIT).parse_weather(input), expected_output_fahrenheit)
        self.assertEqual(OpenWeatherParser(temp_config=FAHRENHEIT_AND_CELSIUS).parse_weather(input), expected_output_both)

    def test_parse_forecast(self):
        input = {
            "cod": "200",
            "message": 0,
            "cnt": 40,
            "list": [
                {
                    "dt": 1635379200,
                    "main": {
                        "temp": 288.4,
                        "feels_like": 287.94,
                        "temp_min": 287.29,
                        "temp_max": 288.4,
                        "pressure": 1008,
                        "sea_level": 1008,
                        "grnd_level": 1001,
                        "humidity": 75,
                        "temp_kf": 1.11
                    },
                    "weather": [
                        {
                            "id": 803,
                            "main": "Clouds",
                            "description": "broken clouds",
                            "icon": "04n"
                        }
                    ],
                    "clouds": {
                        "all": 83
                    },
                    "wind": {
                        "speed": 6.86,
                        "deg": 185,
                        "gust": 15.71
                    },
                    "visibility": 10000,
                    "pop": 0.04,
                    "sys": {
                        "pod": "n"
                    },
                    "dt_txt": "2021-10-28 00:00:00"
                },
                {
                    "dt": 1635390000,
                    "main": {
                        "temp": 287.15,
                        "feels_like": 286.67,
                        "temp_min": 286.25,
                        "temp_max": 287.15,
                        "pressure": 1007,
                        "sea_level": 1007,
                        "grnd_level": 999,
                        "humidity": 79,
                        "temp_kf": 0.9
                    },
                    "weather": [
                        {
                            "id": 804,
                            "main": "Clouds",
                            "description": "overcast clouds",
                            "icon": "04n"
                        }
                    ],
                    "clouds": {
                        "all": 92
                    },
                    "wind": {
                        "speed": 7.06,
                        "deg": 180,
                        "gust": 16.29
                    },
                    "visibility": 10000,
                    "pop": 0.15,
                    "sys": {
                        "pod": "n"
                    },
                    "dt_txt": "2021-10-28 03:00:00"
                }
            ]
        }
        expected_output = [
            {
                "temperature": "59 °F, 15 °C",
                "pressure": "1008 hpa",
                "cloudiness": "Broken clouds",
                "humidity": "75%",
                "datetime": "2021-10-28 00:00:00"
            },
            {
                "temperature": "57 °F, 14 °C",
                "pressure": "1007 hpa",
                "cloudiness": "Overcast clouds",
                "humidity": "79%",
                "datetime": "2021-10-28 03:00:00"
            }
        ]
        self.assertEqual(OpenWeatherParser().parse_forecast(input), expected_output)