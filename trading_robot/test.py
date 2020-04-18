import mock
import sqlalchemy
import random
from conf import config

_pair = 'btc_usd'


def test_process_buy_no_prediction():

    def patched_configure_poloniex1():
        polo = mock.Mock()
        polo.returnCompleteBalances.return_value = {config.get_pair_first_symbol(_pair): {'available': 100.0}}

        return polo

    patch1 = mock.patch('conf.config.DB_PATH', '.{}'.format(random.randint(10000,90000)))
    patch2 = mock.patch('orders_engine_helpers.functions.configure_poloniex', patched_configure_poloniex1)
    with patch1, patch2:
        from orders_engine_helpers import process_buy
        process_buy.process_buy(_pair)


def test_process_buy_true_prediction():

    def patched_configure_poloniex2():
        polo = mock.Mock()
        polo.returnCompleteBalances.return_value = {config.get_pair_first_symbol(_pair): {'available': 100.0}}
        polo.buy.return_value = {'orderNumber': 777777}
        return polo

    patch1 = mock.patch('conf.config.DB_PATH', '.{}'.format(random.randint(10000,90000)))
    patch2 = mock.patch('orders_engine_helpers.process_buy.functions.configure_poloniex', patched_configure_poloniex2)
    with patch1, patch2:
        from orders_engine_helpers import process_buy
        from conf import database_setup as db

        with db.session_scope() as session:
            session.add(
                db.Transaction(
                    pair=_pair,
                    status=config.TransactionStatus.TO_ENQUEUE,
                    ts=100
                )
            )
            session.add(
                db.Price(
                    pair=_pair,
                    buy=20,
                    sell=10,
                    avg=15,
                    ts=100
                )
            )
        process_buy.process_buy(_pair)
