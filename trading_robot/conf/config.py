ESTIMATOR_PATH = '/home/fizzzgen/trading_robot/trading_robot/resources/upstream_estimator.pickle'  # full path to estimator
DB_PATH = '/home/fizzzgen/trading_robot/trading_robot/resources/data'                              # full path to db
STOP_PERCENT = 1.007                                            # stop when price upper then buy_price * STOP_PERCENT
STOP_TIME = 7 * 5 * 60                                 # stop if we reached STOP_TIME
PAIRS = ['USDT_ETH']                                            # working pairs
ORDERBOOK_FORCER_MOVE_PERCENT = 1.00001                         # the percent to move order in stack to reach someone
DROP_BUY_ORDER_DELAY = 3 * 60                            # drop buy order delay, drops order if incompleted
PREDICT_DELAY = 2.5 * 60                                        # period of predict events
MAX_ORDER_PERCENT = 0.1                                         # max amount to buy for one prediction
MINIMAL_AMOUNT = 0.000002


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


class TradeType(object):
    BUY = 0
    SELL = 1


class TradeStatus(object):
    NOT_PROCEESSED = 0
    PROCESSED = 1


class JobType(object):
    PRICE_UPDATE = 0
    PREDICTION_GENERATE = 1
    PROCESS_TRANSACTIONS = 2
    PROCESS_ORDERS = 3
    PROCESS_STOPS = 4
    PROCESS_STATS = 5


def get_pair_first_symbol(pair):
    return pair.split('_')[0]


def get_pair_second_symbol(pair):
    return pair.split('_')[1]

##### Poloniex api keys
API_KEY = '1I2JU38K-YPFH9BFS-FUPMOOXK-Z4R0RF0I'
API_SECRET = 'secret'
