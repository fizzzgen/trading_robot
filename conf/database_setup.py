import sqlite3
import logging

from conf import config


conn = sqlite3.connect(config.DB_PATH)
cur = conn.cursor()

try:
    cur.execute(
        '''CREATE TABLE transactions(
        id INTEGER PRIMARY KEY,
        ts INTEGER,
        ts_performed INTEGER,
        type INTEGER,
        pair TEXT,
        status INTEGER,
        amount REAL,
        price REAL
        );
        '''
    )
except Exception as ex:
    logging.info(ex)

try:
    cur.execute(
        '''CREATE TABLE transactions_history(
        id INTEGER PRIMARY KEY,
        ts INTEGER,
        ts_performed INTEGER,
        type INTEGER,
        pair TEXT,
        status INTEGER,
        amount REAL,
        price REAL
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

try:
    cur.execute(
        '''CREATE TABLE trades(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        price REAL,
        type INTEGER,
        status INTEGER,
        pair TEXT
        );
        '''
    )
except Exception as ex:
    logging.info(ex)

conn.commit()
conn.close()
