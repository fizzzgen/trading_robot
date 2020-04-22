import mock
import random
import datetime
from conf import config

_pair = 'btc_usd'


def test_sell__order_cancel():
    order_number = 1

    def patched_configure_poloniex():
        polo = mock.Mock()
        polo.returnCompleteBalances.return_value = {
            config.get_pair_first_symbol(_pair): {'available': 100.0},
            config.get_pair_second_symbol(_pair): {'available': 100.0},
        }

        polo.returnOpenOrders.return_value = [{'type': 'sell', 'orderNumber': order_number}]
        polo.returnTradeHistory.return_value = []

        return polo

    patch1 = mock.patch('conf.config.DB_PATH', '.{}'.format(random.randint(10000,90000)))
    patch2 = mock.patch('orders_engine_helpers.functions.configure_poloniex', patched_configure_poloniex)
    with patch1, patch2:
        from orders_engine_helpers import process_sell
        from conf import database_setup as db
        with db.session_scope() as session:
            session.add(
                db.Transaction(
                    id=order_number,
                    ts=datetime.datetime.utcnow().timestamp() - config.STOP_TIME - 1,
                )
            )
        process_sell.process_sell(_pair)
        with db.session_scope() as session:
            tr = session.query(db.Transaction).first()
            assert tr.status == config.TransactionStatus.ON_STOP


def test_sell__make_order():
    order_number = 1
    trade_id = 1
    amount = 50


    def patched_configure_poloniex():
        polo = mock.Mock()
        polo.returnCompleteBalances.return_value = {
            config.get_pair_first_symbol(_pair): {'available': 100.0},
            config.get_pair_second_symbol(_pair): {'available': 100.0},
        }
        polo.sell.return_value = {'type': 'sell', 'orderNumber': order_number}
        polo.returnOpenOrders.return_value = []
        polo.returnTradeHistory.return_value = [{'globalTradeID': trade_id, 'amount': amount, 'type': 'buy', 'rate': 1}]

        return polo

    patch1 = mock.patch('conf.config.DB_PATH', '.{}'.format(random.randint(10000,90000)))
    patch2 = mock.patch('orders_engine_helpers.functions.configure_poloniex', patched_configure_poloniex)
    with patch1, patch2:
        from orders_engine_helpers import process_sell
        from conf import database_setup as db
        process_sell.process_sell(_pair)
        with db.session_scope() as session:
            transaction = session.query(db.Transaction).first()
            trade = session.query(db.Trade).first()
            assert transaction.status == config.TransactionStatus.ENQUEUED
            assert trade.id == trade_id
            assert transaction.amount == amount
            assert transaction.type == config.TransactionType.SELL
            assert transaction.id == order_number
