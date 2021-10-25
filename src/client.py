import requests
import json
from .logger import log, WARNING as LOG_WARNING, OK as LOG_OK

#TODO env variables
#os.environ.get('API_KEY')
API_KEY = "cd21bcc54809f9d8d3c8ac821c2501f8"
EXTERNAL_API_BASE_URL = "https://api.openweathermap.org/data/2.5"

# class responsible for fetching weather data from external api
class WeatherClient:

    # PUBLIC METHODS

    def __init__(self):
        self.url = EXTERNAL_API_BASE_URL
        self.api_key = API_KEY
        #self.parser = OpenWeatherParser() TODO
    
    # gets weather and forecast for a location defined by a country code and a city name.
    # validates the country and city parameters to be of the expected format
    
    # Parameters
    #   country: string expected to be of size 2 and lowercase. E.g "co" 
    #   city: string. E.g "Bogota" 

    # Output
    #     dictionanary with data
    #     {
    #        "weather_field_1": "..."
    #        .
    #        .
    #        .
    #        "weather_field_n": "..."
    #        "forecast": {...}
    #     }
    def get_weather(self, country, city):
        self.__validate_city(city)
        self.__validate_country(country)
        current = self.__get_current_weather(country, city)
        forecast = self.__get_forecast(country, city)
        current['forecast'] = forecast
        return current

    # PRIVATE METHODS

    # uses an external api to get current weather for a location, returns dictionary
    # Parameters
    #   country_code: size 2 string, lowercase. E.g "co" 
    #   city: string. E.g "Bogota" 
    def __get_current_weather(self, country_code, city):


        # making request to external api...
        url = "{}/weather".format(self.url)
        params = {
            "q": "{},{}".format(city, country_code),
            "appid": self.api_key 
        }
        log(LOG_OK, "Making current weather request to external API for {}, {}".format(city, country_code))
        response = requests.get(url, params)

        # handling response...
        code = response.status_code
        if code == 200:
            result = json.loads(response.content)
        else:
            # TODO handle failure 
            content = json.loads(response.content)
            if "message" in content:
                log(LOG_WARNING, "Recieved a {} response from external api with message: '{}'".format(code, content['message']))
            else:
                log(LOG_WARNING, "Recieved a {} response from external api".format(code))

            result = {"error": code}
        return result

    # uses an external api to get forecast for a location, returns dictionary
    # Parameters
    #   country_code: size 2 string, lowercase. E.g "co" 
    #   city: string. E.g "Bogota" 
    def __get_forecast(self, country_code, city):
        return {}

    def __validate_city(self, city):
        # TODO
        pass

    def __validate_country(self, country):
        # TODO
        pass
