# -*- coding: utf-8 -*-

"""
------------------------------------------------
describe:
    rest result
    
usage:
    

base_info:
    __version__ = "v.10"
    __author__ = "mingliang.gao"
    __time__ = "2018/9/20"
    __mail__ = "mingliang.gao@qunar.com"
------------------------------------------------
"""

import json


class Status(object):
    def __init__(self, status_id, status, msg, data=None):
        if data is None:
            data = {}
        self.status_body = {
            "status_id": status_id,
            "status": status,
            "msg": msg,
            "data": data,
        }
        self.data = data
        super(Status, self).__init__()

    def json(self):
        return json.dumps(self.status_body)
