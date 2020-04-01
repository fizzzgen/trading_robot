from conf import config
from conf import database_setup
import sqlite3
import time
import datetime
from poloniex import Poloniex

conn = sqlite3.connect(config.DB_PATH)
cur = conn.cursor()

api_key = config.API_KEY
api_secret = config.API_SECRET

polo = Poloniex(api_key, api_secret)

while True:
    time1 = time.time()
    orders = polo.returnOrderBook(currencyPair='all', depth='1')
    for key in orders:
        if key not in config.PAIRS:
            continue

        data = orders[key]
        buy = float(data['asks'][0][0])
        sell = float(data['bids'][0][0])
        avg = (buy + sell) / 2
        ts = datetime.datetime.utcnow().timestamp()
        query = 'INSERT INTO price(ts,avg,buy,sell,pair) VALUES({},{},{},{},"{}")'.format(
            ts, avg, buy, sell, key
        )
        cur.execute(query)
    conn.commit()
    print('TIME:', str(time.time() - time1)[:5], query)


conn.close()
