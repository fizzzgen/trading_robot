import sqlite3
import config


conn = sqlite3.connect(config.DB_PATH)
cur = conn.cursor()

cur.execute(
    '''CREATE TABLE buy_signals(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    info TEXT,
    );
    '''
)

cur.execute(
    '''CREATE TABLE buy_signals_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    info TEXT,
    );
    '''
)

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
    price_performed REAL,
    );
    '''
)

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
    price_performed REAL,
    );
    '''
)

cur.execute(
    '''CREATE TABLE scheduler(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    job_type INTEGER,
    status INTEGER,
    );
    '''
)

cur.execute(
    '''CREATE TABLE price(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    avg REAL,
    buy REAL,
    sell REAL,
    pair TEXT,
    );
    '''
)

conn.commit()
conn.close()
