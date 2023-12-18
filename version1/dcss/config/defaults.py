import configparser

KEYCLOAK_URL = ""
KEYCLOAK_CLIENT_ID = ""
KEYCLOAK_CLIENT_SECRET = ""
BDA_URL = ""

CONF_FILE = "/etc/dcss.conf"

CELERY_BEAT_PATH = '/var/run/celery-beat.db'

REDIS_HOST = '127.0.0.1'

DEFAULT_COLLECTION_INTERVAL = 30

CHANNEL_DICT = {
    '01': 'wattage',
    '05': 'temperature',
}

conf = configparser.ConfigParser()
conf.read(CONF_FILE)

INTERVAL_DICT = {
    '01': conf.get('dcss', 'interval_ch_01', fallback=DEFAULT_COLLECTION_INTERVAL),
    '05': conf.get('dcss', 'interval_ch_05', fallback=DEFAULT_COLLECTION_INTERVAL),
}
