import requests

#TODO env variables
API_KEY = "cd21bcc54809f9d8d3c8ac821c2501f8"
EXTERNAL_API_BASE_URL = "api.openweathermap.org/data/2.5"

# class responsible for fetching weather data from external api
class WeatherClient:

    # PUBLIC METHODS

    def __init__(self):
        self.url = EXTERNAL_API_BASE_URL
        #self.parser = OpenWeatherParser() TODO
    
    # gets weather and forecast for a location defined by a country code and a city name.
    
    # Parameters
    #   country_code: size 2 string, lowercase. E.g "co" 
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
    def get_weather(self, country_code, city):
        current = self.__get_current_weather(country_code, city)
        forecast = self.__get_forecast(country_code, city)
        current['forecast'] = forecast
        return current

    # PRIVATE METHODS

    # uses an external api to get current weather for a location, returns dictionary
    # Parameters
    #   country_code: size 2 string, lowercase. E.g "co" 
    #   city: string. E.g "Bogota" 
    def __get_current_weather(self, country_code, city):
        return {}

    # uses an external api to get forecast for a location, returns dictionary
    def __get_forecast(self, country_code, city):
        return {}
