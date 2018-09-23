# -*- coding: utf-8 -*-

"""
------------------------------------------------
describe:
    refer to db operations

usage:
    class use

base_info:
    __version__ = "v.10"
    __author__ = "mingliang.gao"
    __time__ = "2018/9/20"
    __mail__ = "mingliang.gao@qunar.com"
------------------------------------------------
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from config import DB_DEBUG

BASE = declarative_base()


class CityIdsModal(BASE):
    """
    cityids table modal
    """
    __tablename__ = 'cityids'
    id = Column(Integer, primary_key=True)
    cid = Column(String(30))
    cname = Column(String(30))
    ts = Column(DateTime)


def get_db_session():
    """
    get sqlite db session
    :return: session object
    """
    engine = get_db_connect()
    DBSession = sessionmaker(bind=engine, autocommit=False)
    return DBSession()


def get_db_connect():
    """
    get sqlite db connect
    :return: connect object
    """
    return create_engine('sqlite:///weather.db', echo=DB_DEBUG)


def init_cityids_db():
    """
    initial sqlite db table: cityids
    :return: bool
    """
    BASE.metadata.create_all(get_db_connect())


class CityIdsBo(object):
    """
    city id query modal
    """
    def __init__(self):
        self.session = get_db_session()

    @staticmethod
    def get_new_modal():
        """
        get new cityids modal
        :return: modal
        """
        return CityIdsModal()

    def get_modal_by_name(self, cityname):
        """
        get modal by city name
        :param cityname: city name
        :return: modal or none
        """
        q = self.session.query(CityIdsModal)
        q = q.filter(CityIdsModal.cname == cityname)
        q = q.first()
        if q:
            return q
        else:
            return None

    def get_max_id(self):
        """
        get modal max id value
        :return: id
        """
        q = self.session.query(CityIdsModal)
        q = q.order_by(CityIdsModal.id.desc())
        q = q.first()
        if q:
            return q.id
        else:
            return 0

    def add(self, modal):
        """
        add modal data
        :param modal: cityids modal
        :return: None
        """
        with self.session.begin(subtransactions=True):
            self.session.add(modal)

    def update(self, modal):
        """
        update modal data
        :param modal: cityids modal
        :return: None
        """
        with self.session.begin(subtransactions=True):
            self.session.merge(modal)
