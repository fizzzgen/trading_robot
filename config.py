ESTIMATOR_PATH = 'upstream_estimator.pickle'
DB_PATH = 'data'
STOP_PERCENT = 1.007     # stop when price upper then buy_price * STOP_PERCENT
STOP_TIME = 7 * 5 * 60   # stop if we reached STOP_TIME
PAIRS = ['USDT_ETH']


JobStatus(object):
    ENQUEUED = 0
    EXECUTING = 1
    FINISHED = 2


TransactionType(object):
    BUY = 0
    SELL = 1


TransactionStatus(object):
    ENQUEUED = 0
    ORDERED = 1
    PERFORMED = 2


JobType(object):
    PRICE_UPDATE = 0
    PREDICTION_GENERATE = 1
    PROCESS_TRANSACTIONS = 2
    PROCESS_ORDERS = 3
    PROCESS_STOPS = 4
    PROCESS_STATS = 5
