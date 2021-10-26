from flask import Blueprint, request, Response
import json
from .client import WeatherClient, InvalidParameters
from .logger import log, OK as LOG_OK, ERROR as LOG_ERROR

OK = 200
BAD_REQUEST = 400
INTERNAL_SERVER_ERROR = 500

PATH = "/weather"

weather_handler = Blueprint("weather_handler", __name__)

@weather_handler.route(PATH, methods=['GET'])
def get_weather():
    city = request.args.get("city")
    country = request.args.get("country")
    log(LOG_OK, "Recieved weather request for {}, {}".format(city, country))

    weather_client = WeatherClient()
    try:
        content = weather_client.get_weather(country, city)
        content = json.dumps(content) # FIXME, weather_client should return json-dumped data after caching is added
        status = OK 
    except InvalidParameters as e:
        status = BAD_REQUEST
        content = json.dumps({
            "message": "Invalid parameters. Please make sure that the city and country are valid",
            "errors": e.errors
        })
    except Exception as e:
        log(LOG_ERROR, "Unexpected exception raised when getting weather for {}, {}:\n{}".format(city, country, repr(e)))
        status = INTERNAL_SERVER_ERROR
        content = json.dumps({
            "message": "Something went wrong with your request, please try again later"
        })

    return Response(content, status, mimetype="application/json")