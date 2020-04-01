from conf import config
import coloredlogs
import logging

coloredlogs.install(level='DEBUG')

from conf import database_setup

import sqlite3
import attrdict
import datetime
import time
from poloniex import Poloniex
import logging


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return attrdict.AttrDict(d)


conn = sqlite3.connect(config.DB_PATH)
conn.row_factory = _dict_factory
cur = conn.cursor()

api_key = config.API_KEY
api_secret = config.API_SECRET
polo = Poloniex(api_key, api_secret)

_timing = time.time()


def _arc(f):
    def decorator(*args, **kwargs):
        logging.info(('request', f.__name__, str(args), str(kwargs)))
        while time.time() - _timing < 0.3:
            time.sleep(0.01)
        return f(*args, **kwargs)
    return decorator

polo.buy = _arc(polo.buy)
polo.sell = _arc(polo.sell)
polo.returnCompleteBalances = _arc(polo.returnCompleteBalances)
polo.returnOpenOrders = _arc(polo.returnOpenOrders)
polo.cancelOrder = _arc(polo.cancelOrder)
polo.moveOrder = _arc(polo.moveOrder)
polo.returnTradeHistory = _arc(polo.returnTradeHistory)


def _update_status(transaction_id, status):
    cur.execute('UPDATE transactions SET status={} WHERE id={}'.format(
        status,
        transaction_id,
    ))
    conn.commit()


def process_buy(pair):
    logging.info('START BUY PAIR %s', pair)
    to_enqueue = cur.execute(
        '''
        SELECT * FROM transactions WHERE pair="{pair}" and status={status} ORDER BY id DESC LIMIT 1;
        '''.format(
            pair=pair,
            status=config.TransactionStatus.TO_ENQUEUE,
        )
    ).fetchall()

    if not to_enqueue:
        logging.info('STOP BUY PAIR %s, BUY SKIP: NO PREDICTION', pair)
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
    amount = balance.available * config.MAX_ORDER_PERCENT

    if amount < config.MINIMAL_AMOUNT:
        logging.info('STOP BUY PAIR %s, BUY FAIL: NOT ENOUGH BALANCE', pair)
        return False

    target_price = latest_order.buy * config.ORDERBOOK_FORCER_MOVE_PERCENT

    order_data = polo.buy(pair, target_price, amount)

    cur.execute(
        '''INSERT INTO transactions(
        id, ts, type, pair, status, amount, price
        ) VALUES (
        {id}, {ts}, {type}, "{pair}", {status}, {amount}, {price},
        ) '''.format(
            id=order_data.orderNumber,
            ts=to_enqueue.ts,
            type=config.TransactionType.BUY,
            pair=pair,
            status=config.TransactionStatus.ENQUEUED,
            amount=amount,
            price=target_price,
        )
    )

    conn.commit()
    logging.info('STOP BUY PAIR %s, BUY SUCCESS', pair)
    return True


def move_orders(pair):
    logging.info('START MOVE ORDERS PAIR %s', pair)
    pair_orders = attrdict.AttrDict(polo.returnOpenOrders(currencyPair=pair))
    logging.info("Pair orders %s", pair_orders)
    latest_order = cur.execute(
        '''
        SELECT * FROM price WHERE pair="{}" ORDER BY id DESC LIMIT 1;
        '''.format(pair)
    ).fetchall()[0]

    for order_data in pair_orders:
        if order_data.type == 'buy':
            _move_buy_orders(order_data, latest_order, pair)
        else:
            _move_sell_orders(order_data, latest_order, pair)
    logging.info('STOP MOVE ORDERS PAIR %s', pair)


def _move_buy_orders(order_data, latest_order, pair):
    target_price = latest_order.buy * config.ORDERBOOK_FORCER_MOVE_PERCENT
    try:
        sql_order_data = cur.execute('SELECT * from transactions WHERE id={}'.format(order_data.orderNumber)).fetchall()[0]
        if sql_order_data.ts + config.DROP_BUY_ORDER_DELAY < datetime.datetime.utcnow().timestamp:
            logging.info("Cancelling order {} BY TIME".format(sql_order_data))
            polo.cancelOrder(order_data.orderNumber)
            _update_status(order_data.orderNumber, config.TransactionStatus.CANCELLED)
            conn.commit()
            return

        logging.info('Trying to force order %s', sql_order_data)
        new_order = attrdict.AttrDict(polo.moveOrder(order_data.orderNumber, target_price))
        logging.info('Forcing to target price success')
        cur.execute(
            '''UPDATE transactions SET price={}, id={} WHERE id={}'''.format(
                target_price, new_order.orderNumber, order_data.orderNumber
            )
        )
        conn.commit()
        logging.info('Updating db success')
        return True
    except Exception as ex:
        logging.warn('Exception when forcing to target price', ex)
        return False


def _move_sell_orders(order_data, latest_order, pair):
    target_price = latest_order.buy / config.ORDERBOOK_FORCER_MOVE_PERCENT
    try:
        sql_order_data = cur.execute('SELECT * from transactions WHERE id={}'.format(order_data.orderNumber)).fetchall()[0]
        if sql_order_data.status != config.TransactionStatus.ON_STOP:
            logging.info("Order waits rate stop {}".format(sql_order_data))
            return

        logging.info('Trying to force order', sql_order_data)
        new_order = attrdict.AttrDict(polo.moveOrder(order_data.orderNumber, target_price))
        logging.info('Forcing to target price success')
        cur.execute(
            '''UPDATE transactions SET price={}, id={} WHERE id={}'''.format(
                target_price, new_order.orderNumber, order_data.orderNumber
            )
        )
        conn.commit()
        logging.info('Updating db success')
        return True
    except Exception as ex:
        logging.warn('Exception when forcing to target price', ex)
        return False
    pass


def process_sell(pair):
    # add stop statuses
    logging.info('START SELL PAIR %s', pair)
    pair_orders = attrdict.AttrDict(polo.returnOpenOrders(currencyPair=pair))

    for order_data in pair_orders:
        if order_data.type == 'buy':
            continue
        sql_order_data = cur.execute('SELECT * from transactions WHERE id={}'.format(order_data.orderNumber)).fetchall()[0]
        if sql_order_data.ts + config.STOP_TIME < datetime.datetime.utcnow().timestamp():
            _update_status(order_data.orderNumber, config.TransactionStatus.ON_STOP)

    # reseiving done buy trades & generating new sell transactions
    trades = polo.returnTradeHistory(currencyPair=pair)
    old_sell_trades_ids = [i[0] for i in cur.execute('SELECT id from trades;').fetchall()]
    new_trades = list(
        map(
            attrdict.AttrDict,
            filter(
                lambda tr: tr['globalTradeID'] not in old_sell_trades_ids and tr['type'] == 'buy',
                trades
            )
        )
    )
    balance = attrdict.AttrDict(polo.returnCompleteBalances()[config.get_pair_second_symbol(pair)]).available
    for trade in new_trades:
        can_sell_amount = balance * (trade.rate * config.STOP_PERCENT)
        target_price = trade.rate * config.STOP_PERCENT
        sell_amount = min(trade.amount, can_sell_amount)
        if sell_amount < config.MINIMAL_AMOUNT:
            continue

        order_data = polo.sell(pair, target_price, sell_amount)

        cur.execute(
            '''INSERT INTO transactions(
            id, ts, type, pair, status, amount, price
            ) VALUES (
            {id}, {ts}, {type}, "{pair}", {status}, {amount}, {price},
            ) '''.format(
                id=order_data.orderNumber,
                ts=datetime.datetime.utcnow().timestamp(),
                type=config.TransactionType.SELL,
                pair=pair,
                status=config.TransactionStatus.ENQUEUED,
                amount=sell_amount,
                price=target_price,
            )
        )

        conn.commit()

        balance -= sell_amount

        cur.execute(
            '''INSERT INTO trades(id,ts,price,type,status,pair) VALUES(
            {id},
            {ts},
            {type},
            {status},
            "{pair}"
            )
            '''.format(
                id=trade.globalTradeId,
                ts=datetime.datetime.utcnow().timestamp(),
                type=config.TradeType.BUY,
                status=config.TradeStatus.PROCESSED
            )
        )
        conn.commit()
    logging.info('STOP SELL PAIR %s', pair)


while True:

    for pair in config.PAIRS:
        logging.info('START PROCESS PAIR %s', pair)
        move_orders(pair)
        process_sell(pair)
        process_buy(pair)
        logging.info('FINISH PROCESS PAIR %s', pair)

conn.close()
