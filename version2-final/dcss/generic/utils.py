import requests
import logging
import json
import configparser
import datetime
from influxdb import InfluxDBClient

from dcss.config.defaults import KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET, KEYCLOAK_URL, BDA_URL, CONF_FILE

logger = logging.getLogger(__name__)


class DataShippingClient(object):
    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        self.token = None
        conf_file = kwargs.get('conf_file', CONF_FILE)
        self.conf_file = conf_file

        conf = configparser.ConfigParser()
        conf.read(conf_file)
        username = conf.get('dcss', 'username')
        password = conf.get('dcss', 'password')

        self._login_payload = 'client_id={client_id}&client_secret={bda_secret}&' \
                              'username={user}&password={passwd}&grant_type=password'.\
            format(client_id=KEYCLOAK_CLIENT_ID, bda_secret=KEYCLOAK_CLIENT_SECRET, user=username, passwd=password)

    def _login(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url=KEYCLOAK_URL, headers=headers, data=self._login_payload)

        if response.status_code == 401:
            logger.error('Credentials are not valid. Check your config file')

        elif response.status_code == 200:
            logger.info('Log-in performed successfully')

            try:
                self.token = response.json()['access_token']

            except KeyError:
                logger.error('Error occured while parsing the key')
                self.token = None

        else:
            logger.error('Encountered unexpected status code from HTTP CALL: {}'.format(response.status_code))
        print(response.text)

        return response

    def send_data(self, data_type, data_value, dummy=False):

        logger.info('Sending data of type {data_type} and value {data_value} to BDA'.format(
            data_type=data_type, data_value=data_value
        ))

        if dummy:
            logger.info('Dummy Flag set. Returning.')
            return

        if not self.token:
            logger.info('Token is not set. Attempting to login-in.')
            self._login()

        headers = {
            'Content-type': 'application/json',
            'Authorization': 'bearer {}'.format(self.token)
        }

        # Get current timestamp and format it
        current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        data_payload = json.dumps(
            {
                "entries": [{
                    "key": "message_type",
                    "value": data_type
                }, {
                    "key": "payload",
                    "value": data_value
                },
                {
                    "key": "datetime",
                    "value": current_timestamp
                }
                ],
                "nested": []
            }
        )

        # Try Except 400, 403
        response = requests.request("POST", url=BDA_URL, headers=headers, data=data_payload)

        if response.status_code == 403:
            logger.info('Found 403 while sending data. Attempting to log-in again.')
            self._login()

            headers.update({'Authorization': 'bearer {}'.format(self.token)})

            response = requests.request("POST", url=BDA_URL, headers=headers, data=data_payload)

            if response.status_code == 400:
                logger.error('Found 400 while sending data. Payload was {}'.format(json.dumps(data_payload)))

            elif response.status_code == 200:
                logger.info('Data Shipped successfully')

            else:
                logger.error('Encountered unexpected status code from HTTP CALL: {}'.format(response.status_code))

        elif response.status_code == 400:
            logger.error('Found 400 while sending data. Payload was {}'.format(json.dumps(data_payload)))

        elif response.status_code == 200:
            logger.info('Data Shipped successfully')

        else:
            logger.error('Encountered unexpected status code from HTTP CALL: {}'.format(response.status_code))

        print(response.text)

        return response


class InfluxHelper(object):
    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        self.token = None
        conf_file = kwargs.get('conf_file', CONF_FILE)
        self.conf_file = conf_file

        conf = configparser.ConfigParser()
        conf.read(conf_file)
        ifx_user = conf.get('influxdb', 'user')
        ifx_pass = conf.get('influxdb', 'passwd')
        self.ifx_db = conf.get('influxdb', 'dbname')
        self.measurement = conf.get('influxdb', 'measurement')

        host = conf.get('influxdb', 'host')
        port = conf.get('influxdb', 'port')

        self.cl = InfluxDBClient(host, port, ifx_user, ifx_pass)

    def query(self, channel, interval):
        """
        channel 05 temperature
        channel 01 wattage

        :param channel:
        :param interval: timewindow in seconds
        :return:
        """

        qr_str = """select MEAN("value") from "{}" WHERE ("channel" = '{}') and time > now() - {}s""".format(
            self.measurement, channel, interval
        )

        return self.cl.query(qr_str, database=self.ifx_db)

    def get_mean(self, channel, interval):
        res = [elem for elem in self.query(channel, interval).get_points()]

        try:
            return res[0]['mean']

        except IndexError:
            return None

        except KeyError:
            return None
        
#channel 05 temperature A
#channel 13 temperature B
#channel 21 temperature C
#channel 01 wattage A
#channel 02 wattage B
#channel 03 wattage C
#channel 04 wattage D
#channel Rh humidity