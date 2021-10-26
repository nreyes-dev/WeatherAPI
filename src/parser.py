from .logger import log, WARNING as LOG_WARNING
# temp configurations
FAHRENHEIT_AND_CELSIUS = 0
FAHRENHEIT = 1
CELSIUS = 2

TEMP_CONFIGURATIONS = (CELSIUS, FAHRENHEIT, FAHRENHEIT_AND_CELSIUS)

# TODO get temp config from env var. if not present default to fahrenheit AND celsius

# Class responsible for translating the responses of the Open Weather external API into the format that meets this API's requirements
class OpenWeatherParser:

    def __init__(self, temp_config=0):
        if temp_config not in TEMP_CONFIGURATIONS:
            raise ValueError("trying to initialize parser with invalid temp config '{}'".format(temp_config))
        self.temp_config = temp_config

    # Parses weather response data from a call to the Open Weather external API into a human-readable dictionary 
    # Parameters:
    #   weather: Dictionary with Opean Weather's OK response content for weather
    # Output:
    #   Human-readable dictionary with weather information
    def parse_ok_weather(self, weather):
        if not isinstance(weather, dict):
            raise TypeError("trying to parse weather that isn't a dictionary")
        result = {}
        self.__parse_temperature(weather, result)
        self.__parse_pressure(weather, result)
        self.__parse_cloudiness(weather, result)
        return result
    
    # Parses forecast response data from a call to the Open Weather's forecast external API into a human-readable dictionary 
    # Parameters:
    #   weather: Dictionary list with Opean Weather's OK response content for forecasts
    # Output:
    #   Human-readable dictionary list with forecast information
    def parse_ok_forecast(self, forecast):
        if not isinstance(forecast, dict):
            raise TypeError("trying to parse forecast that isn't a dictionary")
        result = []

        # TODO set limit from env var?
        # each item in the forecast's list is a weather dictionary just like the one from a /weather call but with a date
        for item in forecast['list']:
            if not isinstance(item, dict):
                raise TypeError("parsing a forecast list that has a non-dict item")

            # parsing weather data...
            partial_result = self.parse_ok_weather(item)
            partial_result['datetime'] = item['dt_txt']

            result.append(partial_result)

        return result



    # PARSING FUNCTIONS:
    # the following are impure functions that build the passed-in result dictionary by adding a human-readable field parsed from the weather parameter

    def __parse_temperature(self, weather, result):
        # FIXME wip... simplified for now
        try:
            temperature = weather['main']['temp']
            result['temperature'] = temperature
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


        except KeyError as e:
            log(LOG_WARNING, "key error when parsing weather pressure: {}".format(str(e)))

# TODO tests