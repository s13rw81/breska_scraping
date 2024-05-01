import logging
import os
import sys
from datetime import datetime

BASE_URL = 'https://www.bershka.com'
URL_FOR_DRESSES = BASE_URL + '/ww/women/clothes/dresses-c1010193213.html'
SLEEP_LONG = 10
SLEEP_SHORT = 5

WORKERS = 4

# log file
WS_LOG_PATH = os.path.join(os.path.curdir, "logs")  # '.\\logs'
try:
    os.makedirs(WS_LOG_PATH)
except FileExistsError:
    pass

# logging
log = logging.getLogger("foliox_logger")
log.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s - %(filename)s > %(funcName)s() # %(lineno)d [%(levelname)s] %(message)s')
DATE_FORMAT = "%Y-%m-%d"
TODAY = datetime.now().strftime(DATE_FORMAT)
LOG_FILE = os.path.join(WS_LOG_PATH, f"{TODAY}_logs.log")  # '.\\2023_03_11_10_18_logs.log'
consoleHandler = logging.StreamHandler(stream=sys.stderr)
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)

fileHandler = logging.FileHandler(LOG_FILE)  # '.\\logs/.\\2023_03_11_10_18_logs.log'
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)
