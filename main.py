from src.logger import log, OK as LOG_OK
from flask import Flask
from src.weather_handler import weather_handler

PORT = 8081 # TODO env var
PATH = "/weather"

def main():

    app = Flask(__name__)
    app.register_blueprint(weather_handler)

    app.run(port=PORT)

if __name__ == '__main__':
    main()