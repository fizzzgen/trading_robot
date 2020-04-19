import logging
import datetime
import attrdict
import time

from conf import config
from conf import database_setup as db
from functions import upstream_signal
from poloniex import Poloniex


FIVE_MINS = 5 * 60

api_key = config.API_KEY
api_secret = config.API_SECRET
polo = Poloniex(api_key, api_secret)

while True:
    with db.session_scope() as session:
        for pair in config.PAIRS:

            data = session.query(db.Price).filter(db.Price.pair == pair).order_by(db.Price.ts.desc()).all()

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
            prediction_data = upstream_signal.predict(result)
            logging.info('Prediction classes probability %s', prediction_data.class_proba)
            if prediction_data.buy:
                logging.info('Prediction for pair %s is UP!', pair)
                # deleting old predictions about this pair
                session.query(db.Transaction).filter(
                    db.Transaction.status == config.TransactionStatus.TO_ENQUEUE
                ).filter(
                    db.Transaction.pair == pair
                ).delete()
                # inserting new prediction
                session.add(
                    db.Transaction(
                        id=-1,
                        ts=datetime.datetime.utcnow().timestamp(),
                        type=config.TransactionType.BUY,
                        status=config.TransactionStatus.TO_ENQUEUE,
                        pair=pair,
                    )
                )
                session.commit()
            else:
                logging.info('Prediction for pair %s is none', pair)

    time.sleep(config.PREDICT_DELAY)
