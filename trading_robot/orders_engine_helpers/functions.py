import time
import logging

from poloniex import Poloniex
from conf import config, database_setup as db


def configure_poloniex():
    api_key = config.API_KEY
    api_secret = config.API_SECRET
    polo = Poloniex(api_key, api_secret)

    _timing = time.time()

    def _arc(f):
        def decorator(*args, **kwargs):
            logging.info(('request', f.__name__, str(args), str(kwargs)))
            while time.time() - _timing < 0.5:
                time.sleep(0.01)
            return f(*args, **kwargs)
        return decorator

    polo.buy = _arc(polo.buy)
    polo.sell = _arc(polo.sell)
    polo.returnCompleteBalances = _arc(polo.returnCompleteBalances)
    polo.returnOpenOrders = _arc(polo.returnOpenOrders)
    polo.cancelOrder = _arc(polo.cancelOrder)
    polo.moveOrder = _arc(polo.moveOrder)
    polo.returnTradeHistory = _arc(polo.returnTradeHistory)
    return polo


def _update_status(transaction_id, status):
    with db.session_scope() as session:
        session.query(db.Transaction).filter(
            db.Transaction.id == transaction_id
        ).update({db.Transaction.status: status})


def _get_latest_order(pair):
        with db.session_scope() as session:
            latest_order = session.query(
                db.Price
            ).filter(
                db.Price.pair == pair
            ).order_by(
                db.Price.id.desc()
            ).limit(1).all()[0]
        return latest_order
