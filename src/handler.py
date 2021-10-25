from flask import Blueprint, request, Response
import json
from .client import WeatherClient
from .logger import log, OK as LOG_OK

PATH = "/weather"

weather_handler = Blueprint("weather_handler", __name__)

@weather_handler.route(PATH, methods=['GET'])
def get_weather():
    city = request.args.get("city")
    country = request.args.get("country")
    log(LOG_OK, "Recieved weather request for {}, {}".format(city, country))

    weather_client = WeatherClient()
    response = weather_client.get_weather(city, country)

    return Response(json.dumps(response), status=200, mimetype="application/json")