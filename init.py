# -*- coding: utf-8 -*-

"""
------------------------------------------------
describe:
    api server main method
    
usage:
    python init.py

base_info:
    __version__ = "v.10"
    __author__ = "mingliang.gao"
    __time__ = "2018/9/20"
    __mail__ = "mingliang.gao@qunar.com"
------------------------------------------------
"""
from flask import Flask
from weather import weatherapi
from config import WEB_ADDR, WEB_DEBUG

app = Flask(__name__)
app.register_blueprint(weatherapi)

ADDR = WEB_ADDR


if __name__ == '__main__':
    app.run(host=ADDR[0], port=ADDR[1], debug=WEB_DEBUG)
