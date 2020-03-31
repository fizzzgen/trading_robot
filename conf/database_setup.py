import sqlite3
import logging

from conf import config


conn = sqlite3.connect(config.DB_PATH)
cur = conn.cursor()

try:
    cur.execute(
        '''CREATE TABLE buy_signals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        info TEXT
        );
        '''
    )
except Exception as ex:
    logging.info(ex)

try:
    cur.execute(
        '''CREATE TABLE buy_signals_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        info TEXT
        );
        '''
    )
except Exception as ex:
    logging.info(ex)

try:
    cur.execute(
        '''CREATE TABLE transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        ts_performed INTEGER,
        type INTEGER,
        pair TEXT,
        status INTEGER,
        amount REAL,
        price REAL,
        price_performed REAL
        );
        '''
    )
except Exception as ex:
    logging.info(ex)

try:
    cur.execute(
        '''CREATE TABLE transactions_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        ts_performed INTEGER,
        type INTEGER,
        pair TEXT,
        status INTEGER,
        amount REAL,
        price REAL,
        price_performed REAL
        );
        '''
    )
except Exception as ex:
    logging.info(ex)

try:
    cur.execute(
        '''CREATE TABLE scheduler(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        job_type INTEGER,
        status INTEGER
        );
        '''
    )
except Exception as ex:
    logging.info(ex)

try:
    cur.execute(
        '''CREATE TABLE price(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        avg REAL,
        buy REAL,
        sell REAL,
        pair TEXT
        );
        '''
    )
except Exception as ex:
    logging.info(ex)

conn.commit()
conn.close()
