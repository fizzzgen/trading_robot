import logging
import time
import orders_engine_helpers

from conf import config, database_setup as db
from functions import telegram_log


while True:
    try:
        for pair in config.PAIRS:
            logging.info('START PROCESS PAIR %s', pair)
            orders_engine_helpers.process_move_orders.move_orders(pair)
            orders_engine_helpers.process_sell.process_sell(pair)
            orders_engine_helpers.process_buy.process_buy(pair)
            logging.info('FINISH PROCESS PAIR %s', pair)

        with db.session_scope() as session:
            session.add(db.Sensor(ts=int(time.time() * 1000), type=config.SensorType.ERROR, value=0))

    except Exception as ex:
        with db.session_scope() as session:
            session.add(db.Sensor(ts=int(time.time() * 1000), type=config.SensorType.ERROR, value=100))

        telegram_log.online_log_important('FATAL IN ORDER ENGINE: {}'.format(ex))
        raise
