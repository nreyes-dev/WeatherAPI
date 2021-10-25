from datetime import datetime

OK = 0
WARNING = 1 
ERROR = 2

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
END_COLOR = '\033[0m'

LEVELS = (OK, WARNING, ERROR)

LEVEL_COLORS = {
    OK: GREEN,
    WARNING: YELLOW,
    ERROR: RED,
}

LEVEL_PREFIXES = {
    OK: "",
    WARNING: "Warning: ",
    ERROR: "Error: ",
}

TIMESTAMP_COLOR = BLUE

def log(level, msg):

    if level not in LEVELS:
        raise ValueError("Trying to log with an unknown level value {}", level)

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f"{LEVEL_COLORS[level]}{now} {LEVEL_PREFIXES[level]}{msg}{END_COLOR}")