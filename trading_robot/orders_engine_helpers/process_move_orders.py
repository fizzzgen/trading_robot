import logging
import datetime
import attrdict
import time
from conf import config, database_setup as db
from functions import telegram_log
from . import functions


polo = functions.configure_poloniex()


def move_orders(pair):
    logging.info('START MOVE ORDERS PAIR %s', pair)
    pair_orders = polo.fetch_open_orders(symbol=pair)
    logging.info("Pair orders %s", pair_orders)
    latest_order = functions._get_latest_order(pair)
    telegram_log.online_log("LATEST PRICES" + str(latest_order))
    for order_data in pair_orders:
        order_data = attrdict.AttrDict(order_data)
        order_data.rate = float(order_data.rate)
        order_data.amount = float(order_data.amount)
        if order_data.type == 'buy':
            _move_buy_order(order_data, latest_order, pair)
        else:
            _move_sell_order(order_data, latest_order, pair)
    logging.info('STOP MOVE ORDERS PAIR %s', pair)


def _move_buy_order(order_data, latest_order, pair):

    target_price = float(latest_order.sell) * config.ORDERBOOK_FORCER_MOVE_PERCENT
    try:
        with db.session_scope() as session:
            order_data_query = session.query(db.Transaction).filter(
                db.Transactions.id == (order_data.orderNumber)
            )
            sql_order_data = order_data_query.all()

            if not sql_order_data:
                return

            sql_order_data = sql_order_data[0]
            if sql_order_data.ts + config.DROP_BUY_ORDER_DELAY < datetime.datetime.utcnow().timestamp():
                logging.info("Cancelling order {} BY TIME".format(sql_order_data))
                polo.cancel_order(order_data.orderNumber)
                functions._update_status(order_data.orderNumber, config.TransactionStatus.CANCELLED)
                return

            logging.info('Trying to force order %s', sql_order_data)
            new_order = attrdict.AttrDict(polo.moveOrder(order_data.orderNumber, target_price))
            logging.info('Forcing to target price success')
            order_data_query.update(
                {
                    db.Transaction.price: target_price,
                    db.Transaction.id: new_order.orderNumber
                }
            )
            logging.info('Updating db success')
        return True
    except Exception as ex:
        with db.session_scope() as session:
            session.add(db.Sensor(ts=int(time.time() * 1000), type=config.SensorType.ERROR, value=12))
        logging.warn('Exception when forcing to target price', ex)
        return False


def _move_sell_order(order_data, latest_order, pair):
    target_price = float(latest_order.buy) / config.ORDERBOOK_FORCER_MOVE_PERCENT
    try:
        with db.session_scope() as session:
            order_data_query = session.query(db.Transaction).filter(
                db.Transactions.id == (order_data.orderNumber)
            )
            sql_order_data = order_data_query.all()

            if not sql_order_data:
                return

            sql_order_data = sql_order_data[0]
            if sql_order_data.status != config.TransactionStatus.ON_STOP:
                logging.info("Order waits rate stop {}".format(sql_order_data))
                return

            logging.info('Trying to force order', sql_order_data)
            new_order = attrdict.AttrDict(polo.moveOrder(order_data.orderNumber, target_price))
            logging.info('Forcing to target price success')
            order_data_query.update(
                {
                    db.Transaction.price: target_price,
                    db.Transaction.id: new_order.orderNumber
                }
            )
            logging.info('Updating db success')
        return True
    except Exception as ex:
        with db.session_scope() as session:
            session.add(db.Sensor(ts=int(time.time() * 1000), type=config.SensorType.ERROR, value=11))
        logging.warn('Exception when forcing to target price %s', ex)
        return False
    pass
