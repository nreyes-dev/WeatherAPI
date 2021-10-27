from flask import Flask
from src.handler import weather_handler
import os

DEFAULT_PORT = 8081

def main():

    app = Flask(__name__)
    app.register_blueprint(weather_handler)

    # setting port...
    port=os.environ.get('WAPI_PORT')
    if port is None:
        port=DEFAULT_PORT

    app.run(port=port)

if __name__ == '__main__':
    main()