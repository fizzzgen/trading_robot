from conf import config
from conf import database_setup
from functions import upstream_signal
from poloniex import Poloniex

import sqlite3
import datetime
import attrdict
import time


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return attrdict.AttrDict(d)


conn = sqlite3.connect(config.DB_PATH)
conn.row_factory = dict_factory
cur = conn.cursor()


FIVE_MINS = 5 * 60 * 1000

api_key = config.API_KEY
api_secret = config.API_SECRET
polo = Poloniex(api_key, api_secret)

while True:
    for pair in config.PAIRS:
        data = cur.execute(
            'SELECT avg, ts FROM price WHERE pair="{}" ORDER BY ts DESC'.format(
                pair
            )
        ).fetchall()

        result = []
        latest_ts = data[0].ts + FIVE_MINS

        if latest_ts < datetime.datetime.utcnow().timestamp():
            print('Too old price data')
            continue
        for row in data:
            if row.ts <= latest_ts - FIVE_MINS:
                result.append(row.avg)
                latest_ts -= FIVE_MINS
        result.reverse()
        print(result)
        prediction_data = upstream_signal.predict(result)
        print(prediction_data.class_proba)

        #
        # prediction data format: AttrDict
        # {
        # 'class_proba': predicted,
        # 'buy': predicted_final,
        # 'buy_price': price_history[-1],
        # 'stop_price': config.STOP_PERCENT * price_history[-1],
        # 'stop_utc_time': (
        #     utc_now + datetime.timedelta(seconds=config.STOP_TIME)
        # ),
        # 'utc_time': utc_now,
        # }
        #

        if not prediction_data.buy:
            # deleting old predictions about this pair
            cur.execute('DELETE FROM transactions WHERE status={status} and pair="{pair}"'.format(
                status=config.TransactionStatus.TO_ENQUEUE,
                pair=pair,
            ))
            # inserting new prediction
            cur.execute('INSERT INTO transactions(id, type, status, pair) VALUES(-1, {type}, {status});'.format(
                ts=datetime.datetime.utcnow().timestamp(),
                type=config.TransactionType.BUY,
                status=config.TransactionStatus.TO_ENQUEUE,
            ))
            conn.commit()

    time.sleep(config.PREDICT_DELAY)

conn.close()
