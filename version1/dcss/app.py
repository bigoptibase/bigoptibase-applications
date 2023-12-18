import random

from celery import Celery
import redis
import logging
import time

from dcss.config.defaults import REDIS_HOST, CHANNEL_DICT, INTERVAL_DICT
from dcss.generic.utils import DataShippingClient, InfluxHelper

from dcss import config as celery_conf
from dcss.config import appname

logger = logging.getLogger(__name__)

app = Celery(appname)

app.config_from_object(celery_conf)
app.conf.update()

dsc = DataShippingClient()
red = redis.Redis(host=REDIS_HOST)
ifxh = InfluxHelper()

# CHANNEL_DICT as provided
CHANNEL_DICT = {
    '01': 'wattage',
    '02': 'wattage_2',
    '03': 'wattage_3',
    '04': 'wattage_4',
    '05': 'temperature',
    '13': 'temperature_2',
    '21': 'temperature_3',
    'Rh': 'humidity'
}


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Upload Channel 05 data every 60.0 - Data are collected from influx channel 05 over a window of 60 seconds
    # NOTE THAT: 60.0 (the repeat interval) != 60 ( the time window over which the data are requested from influx )
    # Here it is assumed that COLLECT_INTERVAL == INFLUX_TIMEWINDOW
    # sender.add_periodic_task(60.0, upload_channel_data.s('05', 60), name='Uploading {}'.format(CHANNEL_DICT['05']))

    # Upload Channel 05 - Temperature A
    sender.add_periodic_task(float(INTERVAL_DICT['05']), upload_channel_data.s('05', int(INTERVAL_DICT['05'])),
                             name='Uploading {}'.format(CHANNEL_DICT['05']))

    # Upload Channel 13 - Temperature B
    sender.add_periodic_task(float(INTERVAL_DICT['13']), upload_channel_data.s('13', int(INTERVAL_DICT['13'])),
                             name='Uploading {}'.format(CHANNEL_DICT['13']))

    # Upload Channel 21 - Temperature C
    sender.add_periodic_task(float(INTERVAL_DICT['21']), upload_channel_data.s('21', int(INTERVAL_DICT['21'])),
                             name='Uploading {}'.format(CHANNEL_DICT['21']))

    # Upload Channel 01 - Power A
    sender.add_periodic_task(float(INTERVAL_DICT['01']), upload_channel_data.s('01', int(INTERVAL_DICT['01'])),
                             name='Uploading {}'.format(CHANNEL_DICT['01']))

    # Upload Channel 02 - Power B
    sender.add_periodic_task(float(INTERVAL_DICT['02']), upload_channel_data.s('02', int(INTERVAL_DICT['02'])),
                             name='Uploading {}'.format(CHANNEL_DICT['02']))

    # Upload Channel 03 - Power C
    sender.add_periodic_task(float(INTERVAL_DICT['03']), upload_channel_data.s('03', int(INTERVAL_DICT['03'])),
                            name='Uploading {}'.format(CHANNEL_DICT['03']))

    # Upload Channel 04 - Power D
    sender.add_periodic_task(float(INTERVAL_DICT['04']), upload_channel_data.s('04', int(INTERVAL_DICT['04'])),
                            name='Uploading {}'.format(CHANNEL_DICT['04']))

    # Upload Channel Rh - Humidity
    sender.add_periodic_task(float(INTERVAL_DICT['Rh']), upload_channel_data.s('Rh', int(INTERVAL_DICT['Rh'])),
                             name='Uploading {}'.format(CHANNEL_DICT['Rh']))


@app.task
def collect_temperature():
    temperature_channels = ['05', '13', '21']

    for channel in temperature_channels:
        channel_key = CHANNEL_DICT[channel]  # e.g., 'temperature_1' for channel '05'

        logger.info(f'Collecting Temperature from channel {channel} ({channel_key})')

        # Read value from InfluxDB for the specific channel
        # Implement 'get_latest_value' in InfluxHelper to fetch the latest temperature data
        temp = ifxh.get_latest_value(channel)

        if temp is not None:
            logger.debug(f'Temperature value from channel {channel} ({channel_key}) retrieved: {temp}')
            # Store the value in Redis under the channel-specific key
            red.lpush(channel_key, temp)
        else:
            logger.warning(f'No data retrieved from channel {channel} ({channel_key})')

@app.task
def collect_power():
    power_channels = ['01', '02', '03', '04']

    for channel in power_channels:
        channel_key = CHANNEL_DICT[channel]  # e.g., 'power_1' for channel '01'

        logger.info(f'Collecting Power from channel {channel} ({channel_key})')

        # Read value from InfluxDB for the specific power channel
        # Implement 'get_latest_value' in InfluxHelper to fetch the latest power data
        power = ifxh.get_latest_value(channel)

        if power is not None:
            logger.debug(f'Wattage value from channel {channel} ({channel_key}) retrieved: {power}')
            # Store the value in Redis under the channel-specific key
            red.lpush(channel_key, power)
        else:
            logger.warning(f'No data retrieved from channel {channel} ({channel_key})')

@app.task
def collect_humidity():
    humidity_channel = 'Rh'
    channel_key = CHANNEL_DICT[humidity_channel]  # e.g., 'humidity'

    logger.info(f'Collecting Humidity from channel {humidity_channel} ({channel_key})')

    # Read value from InfluxDB for the humidity channel
    # Implement 'get_latest_value' in InfluxHelper to fetch the latest humidity data
    hum = ifxh.get_latest_value(humidity_channel)

    if hum is not None:
        logger.debug(f'Humidity value from channel {humidity_channel} ({channel_key}) retrieved: {hum}')
        # Store the value in Redis under the channel-specific key
        red.lpush(channel_key, hum)
    else:
        logger.warning(f'No data retrieved from channel {humidity_channel} ({channel_key})')


@app.task
def upload_temperature():
    temperature_channels = ['05', '13', '21']

    for channel in temperature_channels:
        channel_key = CHANNEL_DICT[channel]  # e.g., 'temperature_1' for channel '05'

        logger.info(f'Uploading Temperature data from channel {channel} ({channel_key})')

        # Retrieve Value from REDIS for each temperature channel
        val = red.rpop(channel_key)

        if val is not None:
            try:
                start_time = time.time()
                dsc.send_data(channel_key, val.decode())  # Use channel_key as the data identifier
                logger.debug(f"--- Uploading {channel_key} took {time.time() - start_time} seconds ---")
            except AttributeError:
                logger.warning(f'Value {val} from {channel_key} could not be decoded. Skipping')
        else:
            logger.info(f'No data to upload for {channel_key}')

@app.task
def upload_power():
    power_channels = ['01', '2', '3', '4']

    for channel in power_channels:
        channel_key = CHANNEL_DICT[channel]  # e.g., 'power_1' for channel '01'

        logger.info(f'Uploading Power data from channel {channel} ({channel_key})')

        # Retrieve Value from REDIS for each power channel
        val = red.rpop(channel_key)

        if val is not None:
            try:
                start_time = time.time()
                dsc.send_data(channel_key, val.decode())  # Use channel_key as the data identifier
                logger.debug(f"--- Uploading {channel_key} took {time.time() - start_time} seconds ---")
            except AttributeError:
                logger.warning(f'Value {val} from {channel_key} could not be decoded. Skipping')
        else:
            logger.info(f'No data to upload for {channel_key}')

@app.task
def upload_humidity():
    humidity_channel = 'Rh'
    channel_key = CHANNEL_DICT[humidity_channel]  # e.g., 'humidity' for channel 'Rh'

    logger.info(f'Uploading Humidity data from channel {humidity_channel} ({channel_key})')

    # Retrieve Value from REDIS for the humidity channel
    val = red.rpop(channel_key)

    if val is not None:
        try:
            start_time = time.time()
            dsc.send_data(channel_key, val.decode())  # Use channel_key as the data identifier
            logger.debug(f"--- Uploading {channel_key} took {time.time() - start_time} seconds ---")
        except AttributeError:
            logger.warning(f'Value {val} from {channel_key} could not be decoded. Skipping')
    else:
        logger.info(f'No data to upload for {channel_key}')

@app.task
def upload_channel_data(channel, interval):

    val = ifxh.get_mean(channel, interval)

    data_upl = '{} - {} - {}'.format(val, channel, CHANNEL_DICT[str(channel)])

    logger.info('Uploading Data {}'.format(data_upl))

    if val:
        start_time = time.time()
        dsc.send_data(CHANNEL_DICT[str(channel)], val)
        logger.info("--- Uploading {} took {} seconds ---" .format(data_upl, time.time() - start_time))

    else:
        logger.warning('Value for {} was None'.format(data_upl))
