from conf import config
from conf import database_setup as db
import time
import datetime
from poloniex import Poloniex

api_key = config.API_KEY
api_secret = config.API_SECRET

polo = Poloniex(api_key, api_secret)

while True:
    try:
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
            with db.session_scope() as session:
                session.add(
                    db.Price(
                        ts=ts,
                        avg=avg,
                        buy=buy,
                        sell=sell,
                        pair=key,
                    )
                )
                session.add(
                    db.Sensor(
                        ts=ts * 1000,
                        type=config.SensorType.PRICE,
                        additional=key,
                        value=avg,
                    )
                )
        print('TIME:', str(time.time() - time1)[:5])
    except Exception as ex:
        with db.session_scope() as session:
            session.add(
                    db.Price(
                        ts=ts,
                        avg=avg,
                        buy=buy,
                        sell=sell,
                        pair=key,
                    )
            )
            session.add(
                    db.Sensor(
                        ts=ts * 1000,
                        type=config.SensorType.ERROR,
                        additional=key,
                        value=50,
                    )
            )
