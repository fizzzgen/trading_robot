ESTIMATOR_PATH = 'resources/upstream_estimator.pickle'
DB_PATH = 'resources/data'
STOP_PERCENT = 1.007     # stop when price upper then buy_price * STOP_PERCENT
STOP_TIME = 7 * 5 * 60 * 1000   # stop if we reached STOP_TIME
PAIRS = ['USDT_ETH', 'USDT_BTC']
ORDERBOOK_FORCER_MOVE_PERCENT = 1.00001
DROP_BUY_ORDER_DELAY = 3 * 60 * 1000
PREDICT_DELAY = 2.5 * 60
MAX_ORDER_PERCENT = 0.5


class JobStatus(object):
    ENQUEUED = 0
    EXECUTING = 1
    FINISHED = 2


class TransactionType(object):
    BUY = 0
    SELL = 1


class TransactionStatus(object):
    TO_ENQUEUE = 0
    ENQUEUED = 1
    ON_STOP = 2
    COMPLETED = 3
    CANCELLED = 4


class JobType(object):
    PRICE_UPDATE = 0
    PREDICTION_GENERATE = 1
    PROCESS_TRANSACTIONS = 2
    PROCESS_ORDERS = 3
    PROCESS_STOPS = 4
    PROCESS_STATS = 5

def get_pair_first_symbol(pair):
    return pair.split('_')[0]

API_KEY = '1I2JU38K-YPFH9BFS-FUPMOOXK-Z4R0RF0I'
API_SECRET = 'top secret'
