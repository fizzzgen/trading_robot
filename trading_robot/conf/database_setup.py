import sqlalchemy
import logging

from sqlalchemy import orm
from conf import config
from contextlib import contextmanager
from sqlalchemy.ext.declarative import declarative_base

_engine = sqlalchemy.create_engine('sqlite:///{}'.format(config.DB_PATH))
Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'Transactions',

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    ts = sqlalchemy.Column(sqlalchemy.Integer)
    ts_performed = sqlalchemy.Column(sqlalchemy.Integer)
    type = sqlalchemy.Column(sqlalchemy.Integer)
    pair = sqlalchemy.Column(sqlalchemy.String(32))
    amount = sqlalchemy.Column(sqlalchemy.Float)
    price = sqlalchemy.Column(sqlalchemy.Float)
    status = sqlalchemy.Column(sqlalchemy.Integer)


class Price(Base):
    __tablename__ = 'Price',

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    ts = sqlalchemy.Column(sqlalchemy.Integer)
    avg = sqlalchemy.Column(sqlalchemy.Float)
    buy = sqlalchemy.Column(sqlalchemy.Float)
    sell = sqlalchemy.Column(sqlalchemy.Float)
    pair = sqlalchemy.Column(sqlalchemy.String(32))


class Trade(Base):
    __tablename__ = 'Trades'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    ts = sqlalchemy.Column(sqlalchemy.Integer)
    price = sqlalchemy.Column(sqlalchemy.Float)
    type = sqlalchemy.Column(sqlalchemy.Integer)
    pair = sqlalchemy.Column(sqlalchemy.String(32))
    status = sqlalchemy.Column(sqlalchemy.Integer)


class Sensor(Base):
    __tablename__ = 'Sensors'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    ts = sqlalchemy.Column(sqlalchemy.Integer)
    type = sqlalchemy.Column(sqlalchemy.Integer)
    additional = sqlalchemy.Column(sqlalchemy.String(128))
    value = sqlalchemy.Column(sqlalchemy.Float)

Base.metadata.create_all(_engine)
_session_maker = orm.sessionmaker(bind=_engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = _session_maker()
    try:
        yield session
        session.commit()
    except Exception as ex:
        logging.exception(ex)
        session.rollback()
        raise
    finally:
        session.close()
