import logging
import datetime
import attrdict
import time
from conf import config, database_setup as db
from . import functions


polo = functions.configure_poloniex()


def process_sell(pair):
    # add stop statuses
    logging.info('START SELL PAIR %s', pair)
    with db.session_scope() as session:

        pair_orders = polo.returnOpenOrders(currencyPair=pair)

        for order_data in pair_orders:
            order_data = attrdict.AttrDict(order_data)
            if order_data.type == 'buy':
                continue
            order_data_query = session.query(db.Transaction).filter(
                db.Transaction.id == (order_data.orderNumber)
            )
            sql_order_data = order_data_query.all()
            if not sql_order_data:
                continue
            sql_order_data = sql_order_data[0]

            if sql_order_data.ts + config.STOP_TIME < datetime.datetime.utcnow().timestamp():
                functions._update_status(order_data.orderNumber, config.TransactionStatus.ON_STOP)

        # reseiving done buy trades & generating new sell transactions
        trades = polo.returnTradeHistory(currencyPair=pair)
        old_sell_trades_ids = [i[0] for i in session.query(db.Trade.id).all()]

        new_trades = list(
            map(
                attrdict.AttrDict,
                filter(
                    lambda tr: (
                        tr['globalTradeID'] not in old_sell_trades_ids
                        and tr['type'] == 'buy'
                    ),
                    trades
                )
            )
        )

        balance = attrdict.AttrDict(polo.returnCompleteBalances()[config.get_pair_second_symbol(pair)]).available
        balance = float(balance)
        next_sell_amount = 0.0
        for trade in new_trades:
            logging.exception('processing new trade for selling: %s', trade)
            trade.amount = float(trade.amount)
            trade.rate = float(trade.rate)
            can_sell_amount = balance
            target_price = trade.rate * config.STOP_PERCENT
            sell_amount = min(trade.amount + next_sell_amount, can_sell_amount)
            if sell_amount < config.MINIMAL_AMOUNT:
                next_sell_amount = sell_amount
                logging.exception('sell amount < minimal amount, skipping trade: %s', trade)
                continue
            next_sell_amount = 0

            try:
                order_data = attrdict.AttrDict(polo.sell(pair, target_price, sell_amount))
            except Exception as ex:
                session.add(db.Sensor(ts=int(time.time()*1000), type=config.SensorType.ERROR, value=10))
                logging.info('exception while trying to sell order: %s %s', trade, ex)
                continue
            session.add(
                db.Transaction(
                    id=order_data.orderNumber,
                    ts=datetime.datetime.utcnow().timestamp(),
                    type=config.TransactionType.SELL,
                    pair=pair,
                    status=config.TransactionStatus.ENQUEUED,
                    amount=sell_amount,
                    price=target_price,
                )
            )

            balance -= sell_amount

            session.add(
                db.Trade(
                    id=trade.globalTradeID,
                    ts=datetime.datetime.utcnow().timestamp(),
                    type=config.TradeType.BUY,
                    status=config.TradeStatus.PROCESSED
                )
            )

    logging.info('STOP SELL PAIR %s', pair)
