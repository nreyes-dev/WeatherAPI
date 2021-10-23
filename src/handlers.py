from http.server import BaseHTTPRequestHandler
import json

PATH = "/weather"

class WeatherHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == PATH:
            self.send_response(200)
            response = {
                "hello": "world"
            }
        else:
            self.send_response(404)
            response = {
                "error": "Unknown path"
            }

        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
