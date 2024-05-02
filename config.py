import logging
import os
import sys
from datetime import datetime

BASE_URL = 'https://www.bershka.com'
URL_FOR_DRESSES = BASE_URL + '/ww/women/clothes/dresses-c1010193213.html'
SLEEP_LONG = 10
SLEEP_SHORT = 5
FILE_PATH = "result.json"

WORKERS = 2

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

# cookies
COOKIES = [
    {'name': 'JSESSIONID', 'value': '0000vDayFWcSJPDwCXvGbI9I_YK:1bb2b3rq2', 'domain': 'www.bershka.com', 'path': '/'},
    {'name': 'TS01a8c9e3', 'value': '01ee75b7fa34f7b7e796d1495dec178f65114340b210f8d8a88177d7ac3f8a9795e2e31a8afb717d1b288fa1f29829f721ddc09173',
     'domain': 'www.bershka.com', 'path': '/'},
    {'name': 'IDROSTA', 'value': 'e240a648bdba:1f36b085921514cd8d372ebcc',
     'domain': 'www.bershka.com', 'path': '/'},
    {'name': 'ITXSESSIONID', 'value': '3eee1bea720e5ef6e604ccf00055bc8a',
     'domain': 'www.bershka.com', 'path': '/'},
    {'name': 'BSKSESSION', 'value': '692db9659d3aa7569353c060c72149cf',
     'domain': 'www.bershka.com', 'path': '/'},
    {'name': 'bm_sv',
     'value': '7864A4F382573FEA239FC81079BD26B4~YAAQFSozatDhJyyPAQAAp5qONRdyLrBLH/4vne6i5Pb4LR7080u27bekWjSSlOdGYRbhSWYDgAsRUS6qDgemw/KrIa3+Z7MLWlfofv1cUr/57IYYwxxy4Yu7AHOeaRdeH5Fhp4qtv1dadMzwb+PnjBURZDAcYxtiBZYCuvcnCbsVl85n1KHX8kr0ZkBhKql5XpiVM3mcOQBJxunAxu13VeN3VPnmIgMSdqnzWyA/EN7YAjlBZSrX981eckf9SvWbqJQ=~1',
     'domain': 'www.bershka.com', 'path': '/'},
    {'name': 'bm_mi',
     'value': '8BEEA5D0C1D05B2AD2DB33C042D4DA04~YAAQFSozanngJyyPAQAAB22ONRchJIa5lb0hIchVA46gk470j20BJj52sqW2+i1c811KXvsJb4MLdUL/FK5qXWrhmOvSIMHpqc/0zxN4gr8ebTcjsYa5A6tN9xAfptBb0pHoxbYzYuH5Xx1ubgcwIlThM5xobK2UNZgZRdKNAkbaYNHgzr1QKnAyjofMGPd2gxp2/iIXQIp94IFtM93bDjXgen5RkdKFdcxR3D2ikpQs/XA6glFVzITSQ/IStJtocd9CeLTMiP9eIPWqjJ9RFbHjP3OPwTe6raKTBC5wta9q88XP07lW5BGxgMdcsupUg7hNkY2V4N2nuX9tUdg=~1',
     'domain': 'www.bershka.com', 'path': '/'},
    {'name': 'ak_bmsc',
     'value': 'E8B10AAD3891C39B329FCB7B379C8E62~000000000000000000000000000000~YAAQFSozauHjJyyPAQAA4PKONRelLDvAyl2UnfambUWQIX5v/G7rxx3w2PEbPOnaikKDuDwAqRaKt1rlcDx2aX8sQTdmcFbXXkdJWVPRn1vxst5A4N0mduS1IQdleFeDmHK4pP5hqyq5lZY6rLsLX6eKKvlM8u4uBS5TcK1j6m9ChucPvDtnhaE9siRLDIRjHZ8B+q1VCm88lQqVZ1IfFtkhEEsfrVXdD5DXJ0EKaUCX85UqIm+PDg2xv1aTYAwjFKWcIGoDb0yN1bdLclO+YKjBO2/HWkVrmWCC9fj/xS2kKUT3g8RV98vCZhDtP8sDG5ShTz8hgql2svr33sjAJlZny5jspfRxPn3PZcz4AgkrHeYh9xOoxvXFjJze0hG8gBpoo1+Fq2AndjrnO7K20RBHZg1v1mfYEPqs+JFku69N3T9woErxa+escy0IMd1WvgqdpDRazktaIVIf2V9s91Ira+VsVO7NYCwUMuTu/UI0kLuj3VQpaT5O3zijJc26JmCDD8lLV34EqOmjl2Q+pIIaCLE2IiqQ6tnlKw==',
     'domain': 'www.bershka.com', 'path': '/'},
    {'name': 'bm_sz',
     'value': 'C66BF3B85A4CE98CCE43CD08670A5666~YAAQFSozanvgJyyPAQAAB22ONRfHxAhy/0cGM/UTGZAvVqwkFWXMZqb9z13PPG8zS4jL4sdFmjgQLvhgejqFZyEh4vnoaZKbqxXx2KhEACXU9xU4RrYPe46WcdblR/FOWh/ao6cyvYO1ayvwxpRsVCs0FzMcSQChPUN1vQYLcmM91Lfd5BipSsdaxUbAb9WuE7t1O4oB5DbndEXmXHpwAL4IYqZYl+e3q94N8q9a4E3sjxCtw8xQQ3mdXXcxYskGoMgPxfNRtLDsoR1pt7ntJHPPDLU5pL2tkMTeAGGh0IDTsynjtXZmQur4Q81f8FFWbS71dccPdmz9KPYNZ9QpTwULIejTqslvsp0M8qLkwFOuEJXWtDw2e/6t2KcUyrYFGEthmFCMkUSCprFH9ViI8WGJ04pYB3iKOi2T38lH~3422007~4404281',
     'domain': 'www.bershka.com', 'path': '/'},
    {'name': '_abck',
     'value': 'C5796A6081D763417681BA5D29C8851E~0~YAAQFSozavXYJyyPAQAANY6NNQsMo26wBwhKxSShkvUK4MKT1gzkXXAkHgjhB0chRTUjcoS7Avg2h2QbMsD2wzWL+/6y/H2kEJCN6LXr8r8VeKAuGMZdipIjbMVEQCgi9neFMeefwsG4oghwSLtqpxNXJ3W5cMI4pgULluCZzgvBbVyVIKn2xh9oGcnNIXRukW+J4nQeO8s4WDxcprXHh1Ztbj4XRDOmhPJfBGB+s5tegw1/DKUuFB1Wg9a0u8BxG733ZSpQsi0QOccG7dxsmIu1QHCE+FFFtGzcHF1X+5KNGtrzSS1BOW1d3oY5w1Zi9hd5GYqeziQaZPvEX5e7goq3DuHGXHAEq7uqOVIJ4oneTVwAkyWwXfHv+L7j6KWyxsfsecNlWjSbYgKO1+owiAoVYPZ9yg7M/Q==~-1~-1~-1',
     'domain': 'www.bershka.com', 'path': '/'}
]
