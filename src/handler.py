from flask import Blueprint, request, Response
import json
from .client import WeatherClient, InvalidParameters, InvalidAPIKey, CityNotFound
from .logger import log, OK as LOG_OK, ERROR as LOG_ERROR

OK = 200
BAD_REQUEST = 400
INTERNAL_SERVER_ERROR = 500
NOT_FOUND = 404

PATH = "/weather"

weather_handler = Blueprint("weather_handler", __name__)
weather_client = WeatherClient()

@weather_handler.route(PATH, methods=['GET'])
def get_weather():
    city = request.args.get("city")
    country = request.args.get("country")
    log(LOG_OK, "Recieved weather request for {}, {}".format(city, country))

    try:
        content = weather_client.get_weather(country, city)
        status = OK 
    except InvalidParameters as e:
        status = BAD_REQUEST
        content = json.dumps({
            "message": "Invalid parameters. Please make sure that the city and country are valid",
            "errors": e.errors
        })
    except CityNotFound:
        status = NOT_FOUND
        content = json.dumps({
            "message": "The city you requested was not found. Please double-check both the city and the country or try with another"
        })
    except InvalidAPIKey:
        log(LOG_ERROR, "The WAPI_API_KEY environment variable was set to an invalid value. \
It needs to be a valid OpenWeather appid. If you don't have one, you can get one at: https://home.openweathermap.org/users/sign_up")
        status = INTERNAL_SERVER_ERROR 
        content = json.dumps({
            "message": "Something went wrong with your request, please try again later"
        })

    except Exception as e:
        log(LOG_ERROR, "Unexpected exception raised when getting weather for {}, {}:\n{}".format(city, country, repr(e)))
        status = INTERNAL_SERVER_ERROR
        content = json.dumps({
            "message": "Something went wrong with your request, please try again later"
        })

    return Response(content, status, mimetype="application/json")