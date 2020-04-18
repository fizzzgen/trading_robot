import logging
import attrdict
import time
from conf import config, database_setup as db
from functions import telegram_log
from . import functions


polo = functions.configure_poloniex()


def process_buy(pair):
    logging.info('START BUY PAIR %s', pair)

    with db.session_scope() as session:
        prediction_query = session.query(db.Transaction)
        prediction_query = prediction_query.filter(db.Transaction.pair == pair)
        prediction_query = prediction_query.filter(db.Transaction.status == config.TransactionStatus.TO_ENQUEUE)
        to_enqueue = prediction_query.all()

        balance = attrdict.AttrDict(polo.returnCompleteBalances()[config.get_pair_first_symbol(pair)])
        logging.info(balance)
        balance.available = float(balance.available)

        session.add(
            db.Sensor(
                ts=int(time.time()) * 1000,
                value=balance.available,
                type=config.SensorType.BALANCE
            )
        )

        if not to_enqueue:
            logging.info('STOP BUY PAIR %s, BUY SKIP: NO PREDICTION', pair)
            telegram_log.online_log('BUY: no prediction for pair {} - skip buy'.format(pair))
            return None

        to_enqueue = to_enqueue[0]

        # deleting old predictions
        prediction_query.delete()

        latest_order = functions._get_latest_order(pair)

        target_price = latest_order.sell * config.ORDERBOOK_FORCER_MOVE_PERCENT
        amount = config.ONE_BET / target_price
        if amount < config.MINIMAL_AMOUNT or amount > balance.available:
            logging.info('STOP BUY PAIR %s, BUY FAIL: NOT ENOUGH BALANCE', pair)
            telegram_log.online_log('BUY: prediction is True but not enought balance for pair {} - skip buy'.format(pair))
            return False

        order_data = polo.buy(pair, target_price, amount)
        order_data = attrdict.AttrDict(order_data)

        telegram_log.online_log('BUY: {} - success'.format(pair))
        telegram_log.online_log_important('BUY: Order {}'.format(order_data))

        session.add(
            db.Transaction(
                id=order_data.orderNumber,
                ts=to_enqueue.ts,
                type=config.TransactionType.BUY,
                pair=pair,
                status=config.TransactionStatus.ENQUEUED,
                amount=amount,
                price=target_price,
            )
        )
        logging.info('STOP BUY PAIR %s, BUY SUCCESS', pair)
    return True
