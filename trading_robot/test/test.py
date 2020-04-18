import mock
import sqlalchemy
from conf import config


def test_process_buy():
    with mock.patch('conf.config.DB_PATH', ':memory:'):
        from orders_engine_helpers import process_buy
        process_buy.process_buy('btc_usd')
