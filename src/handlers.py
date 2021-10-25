from http.server import BaseHTTPRequestHandler
import json
from .logger import log, OK as LOG_OK


PATH = "/weather"

class WeatherHandler(BaseHTTPRequestHandler):
    #def __init__(self, weather_client):
        #FIXME ??
        #self.weather_client = weather_client

    def do_GET(self):
        # FIXME path changes when it has query parameters so... (I should probably use another http lib)
        if self.path == PATH:
            response = None
            try:
                log(LOG_OK, "handling request")
                response = self.weather_client.get_weather()
            except AttributeError:
                self.send_response(500)
                response = {
                    "error": "We're having techincal problems, please try again later"
                }
            self.send_response(200)
        else:
            self.send_response(404)
            response = {
                "error": "Unknown path"
            }

        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
