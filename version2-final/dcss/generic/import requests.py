import requests
import json
import sys
import logging
from confluent_kafka import Producer, KafkaException
import urllib3

# Suppress InsecureRequestWarning when making unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration parameters
KAFKA_BROKER = '147.102.4.107:9092'
TOKEN_URL = 'https://iccs-bigdata.cslab.ece.ntua.gr:8443/auth/realms/test_realm/protocol/openid-connect/token'
CLIENT_ID = 'kafka-netmode-producer'
CLIENT_SECRET = 'e8ed6031-8f0e-4080-9796-ab039667dfe1'
GRANT_TYPE = 'client_credentials'

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenProvider(object):
    def __init__(self, client_id, client_secret, grant_type):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_req_payload = {'grant_type': grant_type}

    def token(self):
        token_response = requests.post(TOKEN_URL, data=self.token_req_payload, verify=False, allow_redirects=False, auth=(self.client_id, self.client_secret))
        if token_response.status_code != 200:
            logger.error("Failed to obtain token from the OAuth 2.0 server")
            sys.exit(1)
        logger.info("TokenProvider: Successfully obtained a new token!")
        tokens = json.loads(token_response.text)
        return tokens['access_token']

def confluent_kafka_producer():
    token_provider = TokenProvider(CLIENT_ID, CLIENT_SECRET, GRANT_TYPE)
    config = {
        'bootstrap.servers': KAFKA_BROKER,
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanism': 'OAUTHBEARER',
        'sasl.oauthbearer.config': f"scope=requiredScope principal={CLIENT_ID} extension_token={token_provider.token()}"
    }
    return Producer(config)

def send_to_kafka(topic, data):
    producer = confluent_kafka_producer()
    try:
        # Manually serialize data to JSON
        serialized_data = json.dumps(data).encode('utf-8')
        producer.produce(topic, value=serialized_data)
        producer.flush()
        logger.info(f"Message sent to topic {topic}")
    except KafkaException as e:
        logger.error("Failed to send message to Kafka", exc_info=e)