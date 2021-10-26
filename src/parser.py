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

    # METHODS FOR PARSING CURRENT WEATHER

    # Parses the response of a succesful (200 OK) "/weather" call to the Open Weather external API into a human-readable dictionary 
    # Parameters:
    #   weather: Dictionary with Opean Weather's OK response content for a /weather GET request
    # Output:
    #   Human-readable dictionary with weather information
    def parse_ok_current_weather(self, weather):
        if not isinstance(weather, dict):
            raise TypeError("trying to parse weather that isn't a dictionary")
        result = {}
        self.__parse_weather_temperature(weather, result)
        self.__parse_weather_pressure(weather, result)
        return result

    # PARSING FUNCTIONS:
    # the following are impure functions that build the passed-in result dictionary by adding a human-readable field parsed from the weather parameter

    def __parse_weather_temperature(self, weather, result):
        # FIXME wip... simplified for now
        try:
            temperature = weather['main']['temp']
            result['temperature'] = temperature
        except KeyError as e:
            log(LOG_WARNING, "key error when parsing weather temperature: {}".format(str(e)))

    def __parse_weather_pressure(self, weather, result):
        try:
            pressure = weather['main']['pressure']
            result['pressure'] = "{} hpa".format(pressure)
        except KeyError as e:
            log(LOG_WARNING, "key error when parsing weather pressure: {}".format(str(e)))






    # METHODS FOR PARSING FORECAST

    # TODO
        
        
# TODO tests