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
    '01': 'power_1',
    '02': 'power_2',
    '03': 'power_3',
    '04': 'power_4',
    '05': 'temperature_1',
    '13': 'temperature_2',
    '21': 'temperature_3',
    'Rh': 'humidity'
}

conf = configparser.ConfigParser()
conf.read(CONF_FILE)

INTERVAL_DICT = {
    '01': conf.get('dcss', 'interval_ch_01', fallback=DEFAULT_COLLECTION_INTERVAL),
    '02': conf.get('dcss', 'interval_ch_02', fallback=DEFAULT_COLLECTION_INTERVAL),
    '03': conf.get('dcss', 'interval_ch_03', fallback=DEFAULT_COLLECTION_INTERVAL),
    '04': conf.get('dcss', 'interval_ch_04', fallback=DEFAULT_COLLECTION_INTERVAL),
    '05': conf.get('dcss', 'interval_ch_05', fallback=DEFAULT_COLLECTION_INTERVAL),
    '13': conf.get('dcss', 'interval_ch_13', fallback=DEFAULT_COLLECTION_INTERVAL),
    '21': conf.get('dcss', 'interval_ch_21', fallback=DEFAULT_COLLECTION_INTERVAL),
    'Rh': conf.get('dcss', 'interval_ch_Rh', fallback=DEFAULT_COLLECTION_INTERVAL),
}
