import mock
import random
import logging
import datetime
from conf import config

_pair = 'btc_usd'


def test_buy__order_cancel():
    order_number = 1

    def patched_configure_poloniex():
        polo = mock.Mock()
        polo.returnCompleteBalances.return_value = {
            config.get_pair_first_symbol(_pair): {'available': 100.0},
            config.get_pair_second_symbol(_pair): {'available': 100.0},
        }

        polo.returnOpenOrders.return_value = [{'type': 'buy', 'orderNumber': order_number, 'rate': 1, 'amount': 1}]
        polo.returnTradeHistory.return_value = []
        # polo.moveOrder.return_value = [{'type': 'buy', 'orderNumber': order_number_3, 'rate': 1, 'amount': 1}]
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
                    ts=datetime.datetime.utcnow().timestamp() - config.DROP_BUY_ORDER_DELAY - 1,
                    status=config.TransactionStatus.ON_STOP,
                    type=config.TransactionType.BUY,
                    amount=1,
                    price=1,
                )
            )
        process_move_orders.move_orders(_pair)
        with db.session_scope() as session:
            transaction = session.query(db.Transaction).first()
            assert transaction.status == config.TransactionStatus.CANCELLED


def test_buy__order_move():
    order_number = 1
    order_number2 = 2

    sell_price = 100
    buy_price = 200
    def patched_configure_poloniex():
        polo = mock.Mock()
        polo.returnCompleteBalances.return_value = {
            config.get_pair_first_symbol(_pair): {'available': 100.0},
            config.get_pair_second_symbol(_pair): {'available': 100.0},
        }

        polo.returnOpenOrders.return_value = [{'type': 'buy', 'orderNumber': order_number, 'rate': 1, 'amount': 1}]
        polo.returnTradeHistory.return_value = []
        polo.moveOrder.return_value = {'type': 'buy', 'orderNumber': order_number2, 'rate': 1, 'amount': 1}
        return polo

    patch1 = mock.patch('conf.config.DB_PATH', '.{}'.format(random.randint(10000,90000)))
    patch2 = mock.patch('orders_engine_helpers.functions.configure_poloniex', patched_configure_poloniex)
    with patch1, patch2:
        from orders_engine_helpers import process_move_orders
        from conf import database_setup as db
        with db.session_scope() as session:
            session.add(
                db.Price(
                    buy=buy_price,
                    sell=sell_price,
                    avg=None,
                    pair=_pair,
                )
            )
            session.add(
                db.Transaction(
                    id=order_number,
                    ts=datetime.datetime.utcnow().timestamp() - config.DROP_BUY_ORDER_DELAY + 100,
                    status=config.TransactionStatus.ON_STOP,
                    type=config.TransactionType.BUY,
                    amount=1,
                    price=1,
                )
            )
        process_move_orders.move_orders(_pair)
        with db.session_scope() as session:
            transaction = session.query(db.Transaction).all()
            assert len(transaction) == 1
            assert transaction[0].id == order_number2
            assert transaction[0].price == sell_price * config.ORDERBOOK_FORCER_MOVE_PERCENT
