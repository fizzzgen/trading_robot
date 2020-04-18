import mock
import random
from conf import config

_pair = 'btc_usd'


def test_sell():

    def patched_configure_poloniex1():
        polo = mock.Mock()
        polo.returnCompleteBalances.return_value = {config.get_pair_first_symbol(_pair): {'available': 100.0}}

        return polo

    patch1 = mock.patch('conf.config.DB_PATH', '.{}'.format(random.randint(10000,90000)))
    patch2 = mock.patch('orders_engine_helpers.functions.configure_poloniex', patched_configure_poloniex1)
    with patch1, patch2:
        from orders_engine_helpers import process_sell
        process_sell.process_sell(_pair)
