# -*- coding: utf-8 -*-

"""
------------------------------------------------
describe:
    api weather blue print 
usage:


base_info:
    __version__ = "v.10"
    __author__ = "mingliang.gao"
    __time__ = "2018/9/20"
    __mail__ = "mingliang.gao@qunar.com"
------------------------------------------------
"""
import requests
import json
from flask import Blueprint, request
from rest import Status
from db import CityIdsBo
from utiles import get_cur_time

weatherapi = Blueprint('weather', __name__)


@weatherapi.route('/weather', methods=('GET', 'POST'))
@weatherapi.route('/weather/', methods=('GET', 'POST'))
def weather():
    """
    get weather by city name
    :return: json data
    """
    print request.method
    if request.method == 'GET':
        return Status(101,
                      u'failed',
                      u'not allowed get request method',
                      {}).json()

    POST_PARAMS = ['city']

    rform = request.form
    rjson = request.json
    if rform:
        data = rform
    elif rjson:
        data = rjson
    else:
        data = {}

    if not data:
        return Status(201,
                      u'failed',
                      u'no parameters checked',
                      {}).json()

    for k, v in data.iteritems():
        if k not in POST_PARAMS:
            return Status(202,
                          u'failed',
                          u'%s not allowed parameters' % k,
                          {}).json()
    if not isinstance(data, dict):
        data = json.loads(data)

    city = data.get('city')
    city_modal = CityIdsBo().get_modal_by_name(city)
    if not city_modal:
        return Status(301,
                      u'failed',
                      u'no relevant city weather data',
                      {}).json()

    city_id = getattr(city_modal, 'cid')
    try:
        weatherinfo = _get_weather_by_id(city_id)
        if weatherinfo:
            return Status(0,
                          u'success',
                          u'get weather success',
                          weatherinfo).json()
        else:
            return Status(401,
                          u'failed',
                          u'get weather error',
                          {}).json()
    except Exception as e:
        return Status(402,
                      u'failed',
                      u'get weather buildin error: %s' % e.message,
                      {}).json()


def _get_weather_by_id(cid):
    """
    get city weather informations by city id
    :param cid: city id
    :return: json data
    """
    weatherinfo = dict()
    if not cid:
        return weatherinfo

    subvey_info = __get_survey(cid)
    now_info = __get_nowinfo(cid)

    RET_ATTRS = {
        'city': 'id',               # 城市id
        'cityname': 'name',         # 城市名称
        'temp_cur': 'temp_cur',     # 当前温度
        'temp_max': 'temp_max',     # 最大温度
        'temp_min': 'temp_min',     # 最小温度
        'WD': 'windir',             # 风向
        'WS': 'windlevel',          # 风级
        'wse': 'windspeed',         # 风速
        'SD': 'humidity',           # 湿度
        'weather': 'weather',       # 天气类型
        'aqi_pm25': 'pm'            # 空气质量
    }

    if now_info:
        for k, v in RET_ATTRS.iteritems():
            if not k or not v:
                continue

            if v in ['temp_min', 'temp_max']:
                pass
            elif v == 'temp_cur':
                weatherinfo[v] = now_info.get('temp') + u'℃'
            elif v == 'windspeed':
                weatherinfo[v] = now_info.get(k).split(';')[1]
            else:
                weatherinfo[v] = now_info.get(k)

        if subvey_info:
            temp_max = subvey_info.get('temp')
            temp_min = subvey_info.get('tempn')
            weatherinfo['temp_max'] = temp_max
            weatherinfo['temp_min'] = temp_min

    return weatherinfo


def __get_survey(city_id):
    """
    get city survey information
    :param city_id: city id
    :return: json data
    """
    res = dict()
    if not city_id:
        return res

    cur_time_s = get_cur_time(s=1)
    header = dict()
    header['Accept'] = '*/*'
    header['Accept-Encoding'] = 'gzip, deflate'
    header['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
    header['Cache-Control'] = 'no-cache'
    header['Connection'] = 'keep-alive'
    header['Host'] = 'd1.weather.com.cn'
    header['Pragma'] = 'no-cache'
    header['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
    header['Cookie'] = 'vjuids=6db661561.165f4d91632.0.6efbf4687e87c; vjlast=1537411192.1537411192.30; f_city=%E5%8C%97%E4%BA%AC%7C101010100%7C; UM_distinctid=165f4dbd27272f-0df0cc46b52cea-1033685c-13c680-165f4dbd273370; Hm_lvt_080dabacb001ad3dc8b9b9049b36d43b=1537411193,1537411372,1537412102; Wa_lvt_1=1537411194,1537411372,1537412102; Wa_lpvt_1=1537415241; Hm_lpvt_080dabacb001ad3dc8b9b9049b36d43b=1537415836'

    url = "http://d1.weather.com.cn/dingzhi/%s.html?_=%s" % (city_id, cur_time_s)
    header['Referer'] = 'http://www.weather.com.cn/weather1d/%s.shtml' % str(city_id)

    try:
        resp = requests.get(url, headers=header, timeout=3)
        if resp.status_code == 200:
            res = resp.content.split('=')[1].split(';')[0]
            json_res = json.loads(res, encoding='utf-8')
            weatherinfo = json_res.get('weatherinfo')
            """
            正确数据格式：
                "weatherinfo":{
                    "city":"101010100",
                    "cityname":"北京",
                    "temp":"27℃",
                    "tempn":"16℃",
                    "weather":"多云",
                    "wd":"南风转北风",
                    "ws":"<3级转3级",
                    "weathercode":"d1",
                    "weathercoden":"n1",
                    "fctime":"20180920113000"
                }
            """
            return weatherinfo
    except:
        return res
    else:
        return res


def __get_nowinfo(city_id):
    """
    get city now information
    :param city_id: city id
    :return: json data
    """
    json_res = dict()
    if not city_id:
        return json_res

    cur_time_s = get_cur_time(s=1)
    header = dict()
    header['Accept'] = '*/*'
    header['Accept-Encoding'] = 'gzip, deflate'
    header['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
    header['Cache-Control'] = 'no-cache'
    header['Connection'] = 'keep-alive'
    header['Host'] = 'd1.weather.com.cn'
    header['Pragma'] = 'no-cache'
    header['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
    header['Cookie'] = 'vjuids=6db661561.165f4d91632.0.6efbf4687e87c; vjlast=1537411192.1537411192.30; f_city=%E5%8C%97%E4%BA%AC%7C101010100%7C; UM_distinctid=165f4dbd27272f-0df0cc46b52cea-1033685c-13c680-165f4dbd273370; Hm_lvt_080dabacb001ad3dc8b9b9049b36d43b=1537411193,1537411372,1537412102; Wa_lvt_1=1537411194,1537411372,1537412102; Wa_lpvt_1=1537415241; Hm_lpvt_080dabacb001ad3dc8b9b9049b36d43b=1537415836'

    url = "http://d1.weather.com.cn/sk_2d/%s.html?_=%s" % (city_id, cur_time_s)
    header['Referer'] = 'http://www.weather.com.cn/weather1d/%s.shtml' % str(city_id)

    try:
        resp = requests.get(url, headers=header, timeout=3)
        if resp.status_code == 200:
            res = resp.content.split(' = ')[1]
            json_res = json.loads(res, encoding='utf-8')
            """
            正确数据格式：
                {
                    "nameen":"beijing",
                    "cityname":"北京",
                    "city":"101010100",
                    "temp":"22",
                    "tempf":"71",
                    "WD":"西北风",
                    "wde":"NW",
                    "WS":"3级",
                    "wse":"<12km/h",
                    "SD":"25%",
                    "time":"12:05",
                    "weather":"晴",
                    "weathere":"Sunny",
                    "weathercode":"d00",
                    "qy":"1015",
                    "njd":"35km",
                    "sd":"25%",
                    "rain":"0.0",
                    "rain24h":"0",
                    "aqi":"29",
                    "limitnumber":"不限行",
                    "aqi_pm25":"29",
                    "date":"09月23日(星期日)"
                }
            """
            return json_res
    except:
        return json_res
    else:
        return json_res
