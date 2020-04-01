from conf import config
from conf import database_setup

import sqlite3
import attrdict
import datetime
from poloniex import Poloniex


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return attrdict.AttrDict(d)


conn = sqlite3.connect(config.DB_PATH)
conn.row_factory = dict_factory
cur = conn.cursor()

api_key = config.API_KEY
api_secret = config.API_SECRET
polo = Poloniex(api_key, api_secret)


def process_to_enqueue_transactions(pair):
    to_enqueue = cur.execute(
        '''
        SELECT * FROM transactions WHERE pair="{pair}" and status={status} ORDER BY id DESC LIMIT 1;
        '''.format(
            pair=pair,
            status=config.TransactionStatus.TO_ENQUEUE,
        )
    ).fetchall()

    if not to_enqueue:
        return None

    to_enqueue = to_enqueue[0]

    # deleting old predictions
    cur.execute('DELETE FROM transactions WHERE status={status} and pair="{pair}"'.format(
        status=config.TransactionStatus.TO_ENQUEUE,
        pair=pair,
    ))
    conn.commit()

    latest_order = cur.execute(
        '''
        SELECT * FROM price WHERE pair="{}" ORDER BY id DESC LIMIT 1;
        '''.format(pair)
    ).fetchall()[0]

    balance = attrdict.AttrDict(polo.returnCompleteBalances()[config.get_pair_first_symbol(pair)])
    amount = balance.avalible * config.MAX_ORDER_PERCENT
    target_price = latest_order.buy * config.ORDERBOOK_FORCER_MOVE_PERCENT

    order_data = polo.buy(pair, target_price, amount)

    cur.execute(
        '''INSERT INTO transactions(
        id, ts, type, pair, status, amount, price
        ) VALUES (
        {id}, {ts}, {type}, "{pair}", {status}, {amount}, {price},
        ) '''.format(
            id=order_data.id,
            ts=to_enqueue.ts,
            type=config.TransactionType.BUY,
            pair=pair,
            status=config.TransactionStatus.ENQUEUED,
            amount=amount,
            price=target_price,
        )
    )

    conn.commit()
    return True


def process_buy_transactions(pair):
    pair_orders = attrdict.AttrDict(polo.returnOpenOrders(currencyPair=pair))
    print("Pair orders", pair_orders)
    latest_order = cur.execute(
        '''
        SELECT * FROM price WHERE pair="{}" ORDER BY id DESC LIMIT 1;
        '''.format(pair)
    ).fetchall()[0]
    print(latest_order)

    for order_data in pair_orders:
        if order_data.type == 'buy':
            target_price = latest_order.buy * config.ORDERBOOK_FORCER_MOVE_PERCENT
        else:
            continue
        try:
            sql_order_data = cur.execute('SELECT * from transactions WHERE id={}'.format(order_data.orderNumber)).fetchall()[0]

            if sql_order_data.ts + config.DROP_BUY_ORDER_DELAY < datetime.datetime.utcnow().timestamp:
                print("Cancelling order {} BY TIME".format(sql_order_data))
                polo.cancelOrder(order_data.orderNumber)
                cur.execute('UPDATE transactions SET status={} WHERE id={}'.format(
                    config.TransactionStatus.CANCELLED,
                    order_data.orderNumber,
                ))
                conn.commit()
                continue
            
            print ('Trying to force order', sql_order_data)
            new_order = attrdict.AttrDict(polo.moveOrder(order_id, target_price))
            print('Forcing to target price success')
            cur.execute(
                '''UPDATE transactions SET price={}, id={} WHERE id={}'''.format(
                    target_price, new_order.orderNumber, order_data.orderNumber
                )
            )
            conn.commit()
            print('Updating db success')
        except Exception as ex:
            print('Exception when forcing to target price', ex)


def process_sell_transactions(pair):
    pair_orders = attrdict.AttrDict(polo.returnOpenOrders(currencyPair=pair))
    for order_data in pair_orders:
        if order_data.type == 'buy':
            continue


def process_stops(pair):
    pass


while True:

    for pair in config.PAIRS:
        try:
            process_to_enqueue_transactions(pair)
        except Exception as ex:
            print("FATAL", ex)

        try:
            process_buy_transactions(pair)

        except Exception as ex:
            print("FATAL", ex)
        try:
            process_sell_transactions(pair)

        except Exception as ex:
            print("FATAL", ex)
        try:
            process_stops(pair)

        except Exception as ex:
            print("FATAL", ex)

conn.close()
