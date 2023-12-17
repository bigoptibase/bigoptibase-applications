import configparser

KEYCLOAK_URL = "https://iccs-bigdata.cslab.ece.ntua.gr:8443/auth/realms/test_realm/protocol/openid-connect/token"
KEYCLOAK_CLIENT_ID = "bda_client"
KEYCLOAK_CLIENT_SECRET = "bda_secret"
BDA_URL = "https://iccs-bigdata.cslab.ece.ntua.gr:9999/api/datastore/bigoptibase"

CONF_FILE = "/etc/dcss.conf"

CELERY_BEAT_PATH = '/var/run/celery-beat.db'

REDIS_HOST = '127.0.0.1'

DEFAULT_COLLECTION_INTERVAL = 30

CHANNEL_DICT = {
    '01': 'power',
    '05': 'temperature_1',
    '13': 'temperature_2'
}

conf = configparser.ConfigParser()
conf.read(CONF_FILE)

INTERVAL_DICT = {
    '01': conf.get('dcss', 'interval_ch_01', fallback=DEFAULT_COLLECTION_INTERVAL),
    '05': conf.get('dcss', 'interval_ch_05', fallback=DEFAULT_COLLECTION_INTERVAL),
    '13': conf.get('dcss', 'interval_ch_13', fallback=DEFAULT_COLLECTION_INTERVAL),
}