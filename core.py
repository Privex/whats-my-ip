"""
Initialisation file - loads settings from environment, configures logging, enables CORS,
and exposes methods for obtaining instances of Redis/GeoIP2.

Copyright::

    +===================================================+
    |                 © 2019 Privex Inc.                |
    |               https://www.privex.io               |
    +===================================================+
    |                                                   |
    |        IP Address Information Tool                |
    |                                                   |
    |        Core Developer(s):                         |
    |                                                   |
    |          (+)  Chris (@someguy123) [Privex]        |
    |                                                   |
    +===================================================+


"""
from flask import Flask, request
from privex.helpers import env_bool, empty
from privex.loghelper import LogHelper
from os import environ, getenv as env
from os.path import join, dirname, abspath
from geoip2.database import Reader as G2Reader
from enum import Enum
from flask_cors import CORS
import dotenv
import redis
import logging

dotenv.load_dotenv()

BASE_DIR = dirname(abspath(__file__))

app = Flask(__name__)
CORS(app)
cf = app.config

#######################################
#
# General configuration
#
#######################################
cf['DEBUG'] = DEBUG = env_bool('DEBUG', True if env('FLASK_ENV') == 'development' else False)

HOST = cf['HOST'] = env('HOST', '127.0.0.1')
PORT = cf['PORT'] = int(env('PORT', 5111))

cf['API_ONLY'] = env_bool('API_ONLY', False)
"""If set to ``True``, will always return JSON, never HTML pages."""

USE_IP_HEADER = cf['USE_IP_HEADER'] = env_bool('USE_IP_HEADER', True)
"""If set to False, will obtain the IP from request.remote_addr instead of the header set in IP_HEADER"""
IP_HEADER = cf['IP_HEADER'] = env('IP_HEADER', 'X-REAL-IP')
"""The name of the header that will be passed to Flask containing the IP address of the user"""

# To be able to detect both a user's IPv4 and IPv6 addresses, you must have two subdomains
# with the ipv4 subdomain having only an A record, and the ipv6 subdomain with only an AAAA.
V6_HOST = cf['V6_HOST'] = env('V6_HOST', 'ipv6.myip.privex.io')
V4_HOST = cf['V4_HOST'] = env('V4_HOST', 'ipv4.myip.privex.io')

cf['GEOIP_PATH'] = GEOIP_PATH = env('GEOIP_PATH', '/usr/local/var/GeoIP')
"""An absolute path to the GeoIP2 folder containing mmdb files to use for IP lookups (NO ENDING SLASH)"""
cf['GEOIP_PREFIX'] = GEOIP_PREFIX = env('GEOIP_PREFIX', 'GeoLite2-')
"""The prefix for the GeoIP2 files, generally either 'GeoIP2-' for paid, or 'GeoLite2-' for the free edition"""
cf['GEOIP_CACHE_SEC'] = GEOIP_CACHE_SEC = int(env('GEOIP_CACHE_SEC', 600))
"""Amount of seconds to cache GeoIP data in Redis for. Default is 600 seconds (10 minutes)"""

REDIS_HOST = env('REDIS_HOST', 'localhost')
REDIS_PORT = int(env('REDIS_PORT', 6379))

#######################################
#
# Logging configuration
#
#######################################
# Log to console with LOG_LEVEL, as well as output logs >=info / >=warning to respective files
# with automatic daily log rotation (up to 14 days of logs)
# Due to the amount of output from logging.DEBUG, we only log INFO and higher to a file.
# Valid environment log levels (from least to most severe) are:
# DEBUG, INFO, WARNING, ERROR, FATAL, CRITICAL

lh = LogHelper('privex.myip')

LOG_LEVEL = env('LOG_LEVEL', None)
LOG_LEVEL = logging.getLevelName(str(LOG_LEVEL).upper()) if LOG_LEVEL is not None else None

if empty(LOG_LEVEL):
    LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

lh.add_console_handler(level=LOG_LEVEL)

DBG_LOG, ERR_LOG = join(BASE_DIR, 'logs', 'debug.log'), join(BASE_DIR, 'logs', 'error.log')
lh.add_timed_file_handler(DBG_LOG, when='D', interval=1, backups=14, level=LOG_LEVEL)
lh.add_timed_file_handler(ERR_LOG, when='D', interval=1, backups=14, level=logging.WARNING)

log = lh.get_logger()

#######################################
#
# Functions to initialise various
# connections
#
#######################################

_STORE = {}
"""This dictionary stores instances of various connection classes, such as Redis and GeoIP2"""

def get_redis() -> redis.Redis:
    """Initialise or obtain a Redis instance from _STORE"""
    if 'redis' not in _STORE:
        _STORE['redis'] = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    return _STORE['redis']

class GeoType(Enum):
    ASN = f'{GEOIP_PREFIX}ASN.mmdb'
    COUNTRY = f'{GEOIP_PREFIX}Country.mmdb'
    CITY = f'{GEOIP_PREFIX}City.mmdb'

def get_geoip(gtype: GeoType = GeoType.CITY) -> G2Reader:
    """
    Initialise or obtain a GeoIP2 Reader instance from _STORE
    
    :param GeoType gtype: The type of GeoIP2 database to load (ASN/City/Country), e.g. ``GeoType.ASN``
    :return geoip2.database.Reader G2Reader: An instance of :class:`geoip2.database.Reader` for looking up IPv4/v6 addresses.

    """
    gtype = str(gtype.value)
    l = f'geoip_{gtype}'
    if l not in _STORE:
        _STORE[l] = G2Reader(join(GEOIP_PATH, gtype))
    return _STORE[l]
