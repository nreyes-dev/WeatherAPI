from http.server import HTTPServer
from src.handlers import WeatherHandler
from src.weather_client import WeatherClient
from src.logger import log, OK as LOG_OK

def main():
    PORT = 8081 # TODO env var
    weather_client = WeatherClient()
    server = HTTPServer(('', PORT), WeatherHandler(weather_client))
    log(LOG_OK, "WeatherAPI running on port {}".format(PORT))
    server.serve_forever()

if __name__ == '__main__':
    main()