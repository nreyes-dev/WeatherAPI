from http.server import HTTPServer
from src.handlers import WeatherHandler

def main():
    PORT = 8080 # TODO env var
    server = HTTPServer(('', PORT), WeatherHandler)
    print("WeatherAPI running on port {}".format(PORT))
    server.serve_forever()


if __name__ == '__main__':
    main()