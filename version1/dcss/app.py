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


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Upload Channel 05 data every 60.0 - Data are collected from influx channel 05 over a window of 60 seconds
    # NOTE THAT: 60.0 (the repeat interval) != 60 ( the time window over which the data are requested from influx )
    # Here it is assumed that COLLECT_INTERVAL == INFLUX_TIMEWINDOW
    # sender.add_periodic_task(60.0, upload_channel_data.s('05', 60), name='Uploading {}'.format(CHANNEL_DICT['05']))

    sender.add_periodic_task(float(INTERVAL_DICT['05']), upload_channel_data.s('05', int(INTERVAL_DICT['05'])),
                             name='Uploading {}'.format(CHANNEL_DICT['05']))

    # Upload Channel 13
    sender.add_periodic_task(float(INTERVAL_DICT['13']), upload_channel_data.s('13', int(INTERVAL_DICT['05'])),
                             name='Uploading {}'.format(CHANNEL_DICT['13']))

    # Upload Channel 01
    sender.add_periodic_task(
        float(INTERVAL_DICT['01']),
        upload_channel_data.s('01', int(INTERVAL_DICT['01'])),
        name='Uploading {}'.format(CHANNEL_DICT['01'])
    )


@app.task
def collect_temperature():
    logger.info('Collecting Temperature')

    # Read Value from the platform/influx/wherever
    # TODO @DPANTAZATOS
    # Currently retrieving a random number
    temp = round(random.uniform(28.0, 36.0), 2)

    logger.debug('Temperature value retrieved: {}'.format(temp))

    # Store Value to Redis
    red.lpush('temperature', temp)


@app.task
def collect_humidity():
    logger.info('Collecting Humidity')

    # Read Value from the platform/influx/wherever
    # Currently retrieving a random number
    hum = round(random.uniform(58.0, 78.0), 2)

    logger.debug('Humidity value retrieved: {}'.format(hum))

    # Store Value to Redis
    red.lpush('humidity', hum)


@app.task
def upload_temperature():
    logger.info('Uploading Temperature')

    # Retrieve Value from REDIS
    val = red.rpop('temperature')

    try:
        start_time = time.time()
        dsc.send_data('temperature', val.decode())
        logger.debug("--- Uploading temperature took %s seconds ---" % (time.time() - start_time))

    except AttributeError:
        logger.warning('Value {} could not be decoded. Skipping'.format(val))


@app.task
def upload_humidity():
    logger.info('Uploading Humidity')

    # Retrieve Value from REDIS
    val = red.rpop('humidity')

    try:
        start_time = time.time()
        dsc.send_data('humidity', val.decode())
        logger.debug("--- Uploading humidity took %s seconds ---" % (time.time() - start_time))

    except AttributeError:
        logger.warning('Value {} could not be decoded. Skipping'.format(val))


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
