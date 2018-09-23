# -*- coding: utf-8 -*-

"""
------------------------------------------------
describe:
    comment utiles collection
    
usage:
    import 

base_info:
    __version__ = "v.10"
    __author__ = "mingliang.gao"
    __time__ = "2018/9/20"
    __mail__ = "mingliang.gao@qunar.com"
------------------------------------------------
"""
import os
import time
from datetime import datetime
import multiprocessing


def get_cur_time(format='%Y-%m-%d %H:%M:%S', s=None):
    """
    get current time 
    :param format: time format
    :param s: is or not s
    :return: string
    """
    if s:
        return int(time.time() * 1000)
    else:
        return d2s(datetime.now(), format)


def s2d(s, fmt="%Y-%m-%d %H:%M:%S"):
    """
    string time transfer to datetime type 
    :param s: time string 
    :param fmt: time formatter
    :return: datetime 
    """
    return datetime.strptime(s, fmt)


def d2s(d, fmt="%Y-%m-%d %H:%M:%S"):
    """
    datetime type transfer to string time
    :param d: time  
    :param fmt: time formatter
    :return: string time 
    """
    return d.strftime(fmt)


def get_core_in():
    """
    get local server cpu core count
    :return: num
    """
    return multiprocessing.cpu_count()


def get_cur_dir():
    """
    get current file dir
    :return: path
    """
    return os.path.abspath(os.path.dirname(os.path.abspath(__file__)))


def is_exist_db():
    """
    judge use db 
    :return: bool
    """
    cur_dir = get_cur_dir()
    db = os.path.join(cur_dir, 'weather.db')
    if os.path.exists(db):
        return True
    else:
        return False
