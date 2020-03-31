from conf import config
from conf import database_setup
import sqlite3
import requests
import json
import logging
import datetime

conn = sqlite3.connect(config.DB_PATH)
cur = conn.cursor()

for pair in config.PAIRS:
    url = 'https://poloniex.com/public?command=returnOrderBook&currencyPair={}&depth=1'.format(pair)
    data = json.loads(requests.get(url).text)
    print(data)
    buy = float(data['asks'][0][0])
    sell = float(data['bids'][0][0])
    avg = (buy + sell) / 2
    ts = datetime.datetime.utcnow().timestamp()
    query = 'INSERT INTO price(ts,avg,buy,sell,pair) VALUES({},{},{},{},"{}")'.format(
        ts, avg, buy, sell, pair
    )
    logging.info(query)
    cur.execute(query)
    conn.commit()


conn.close()
