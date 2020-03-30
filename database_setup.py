import sqlite3
import config


conn = sqlite3.connect(config.DB_PATH)
cur = conn.cursor()

cur.execute(
    '''CREATE TABLE buy_signals(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    info TEXT
    );
    '''
)

cur.execute(
    '''CREATE TABLE buy_signals_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    info TEXT
    );
    '''
)

cur.execute(
    '''CREATE TABLE transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    info TEXT
    );
    '''
)

cur.execute(
    '''CREATE TABLE transactions_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    info TEXT
    );
    '''
)

cur.execute(
    '''CREATE TABLE scheduler(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    info TEXT,
    );
    '''
)

cur.execute(
    '''CREATE TABLE price(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    info TEXT,
    );
    '''
)

conn.commit()
conn.close()
