import mock
import random
import datetime
from conf import config

_pair = 'btc_usd'


def test_sell__order_cancel():
    order_number = 1
    order_number_2 = 2

    def patched_configure_poloniex():
        polo = mock.Mock()
        polo.returnCompleteBalances.return_value = {
            config.get_pair_first_symbol(_pair): {'available': 100.0},
            config.get_pair_second_symbol(_pair): {'available': 100.0},
        }

        polo.returnOpenOrders.return_value = [{'type': 'sell', 'orderNumber': order_number, 'rate': 1, 'amount': 1}]
        polo.returnTradeHistory.return_value = []

        return polo

    patch1 = mock.patch('conf.config.DB_PATH', '.{}'.format(random.randint(10000,90000)))
    patch2 = mock.patch('orders_engine_helpers.functions.configure_poloniex', patched_configure_poloniex)
    with patch1, patch2:
        from orders_engine_helpers import process_move_orders
        from conf import database_setup as db
        with db.session_scope() as session:
            session.add(
                db.Price(
                    buy=200,
                    sell=100,
                    avg=150,
                    pair=_pair,
                )
            )
            session.add(
                db.Transaction(
                    id=order_number,
                    ts=datetime.datetime.utcnow().timestamp() - config.STOP_TIME - 1,
                    status=config.TransactionStatus.ON_STOP,
                    type=config.TransactionType.SELL,
                )
            )
            session.add(
                db.Transaction(
                    id=order_number_2,
                    ts=datetime.datetime.utcnow().timestamp() - config.STOP_TIME - 1,
                    status=config.TransactionStatus.ON_STOP,
                    type=config.TransactionType.BUY,
                )
            )
        process_move_orders.move_orders(_pair)
