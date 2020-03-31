from conf import config
from conf import database_setup

import sqlite3
from poloniex import Poloniex


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


conn = sqlite3.connect(config.DB_PATH)
conn.row_factory = dict_factory
cur = conn.cursor()

api_key = config.API_KEY
api_secret = config.API_SECRET
polo = Poloniex(api_key, api_secret)


while True:

    for pair in config.PAIRS:

        pair_orders = polo.returnOpenOrders(currencyPair=pair)
        print("Pair orders", pair_orders)
        latest_orderbooks = cur.execute(
            '''
            SELECT * FROM price WHERE pair="{}" ORDER BY id DESC LIMIT 1;
            '''.format(pair)
        ).fetchall()
        print(latest_orderbooks)

        for order_data in pair_orders:
            if order_data['type'] == 'buy':
                target_price = latest_orderbooks['buy'] * (1 + config.ORDERBOOK_FORCER_MOVE_PERCENT)
                order_id = order_data['id']
            else:
                target_price = latest_orderbooks['sell'] * (1 - config.ORDERBOOK_FORCER_MOVE_PERCENT)
                order_id = order_data['id']
            try:
                polo.moveOrder(order_id, target_price)
                print('Forcing to target price success')
                cur.execute('''UPDATE orders SET price={} WHERE id={}'''.format(target_price, order_id))
                conn.commit()
                print('Updating db success')
            except Exception as ex:
                print('Exception when forcing to target price', ex)



conn.close()
