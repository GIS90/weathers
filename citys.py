# -*- coding: utf-8 -*-

"""
------------------------------------------------
describe:
    request get city mapping id 
    
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
import multiprocessing
from utiles import get_core_in, get_cur_time, s2d
from utiles import is_exist_db
from db import CityIdsModal, CityIdsBo
from db import init_cityids_db


POOL_MAX_NUM = get_core_in() + 1
# 最小
PROVINCE_ID_MIN = 101010100
# 非直辖市
# PROVINCE_ID_MIN = 101050100
PROVINCE_ID_MAX = 101350100


class city_src(object):
    """
    city src datasource
    """
    def __init__(self):
        self.citybo = CityIdsBo()
        self.__init_db()

    def __init_db(self):
        """
        initialize db
        :return: None
        """
        if not is_exist_db():
            print '========== create sqlite db ...... =========='
            init_cityids_db()
            print '================ end db ...... =============='

    def run(self):
        """
        initialize city source data 
        to get tianqiwang data
        :return: None
        """
        print '===================city collect start================='

        pool = multiprocessing.Pool(processes=POOL_MAX_NUM)

        all_city_ids = range(PROVINCE_ID_MIN, PROVINCE_ID_MAX)

        for k, v in enumerate(all_city_ids):
            vv = str(v)
            prov_flag = vv[3:5]
            # 直辖市
            if prov_flag in ['01', '02', '03', '04']:
                sub_flag = vv[-2:]
                if sub_flag == '00':
                    self._deal_city(v)
            elif prov_flag == '35':
                pass
            # 非直辖市
            else:
                city_flag = int(vv[5:7])
                if city_flag < 23:
                    self._deal_city(v)
            # pool.apply(self._deal_city, args=(v, ))
        else:
            # pool.close()
            # pool.join()
            print '===================city collect end================='

    def _deal_city(self, city_id):
        """
        buildin deal api request weather informations
        :param city_id: request city id
        :return: None
        """
        if not city_id:
            return

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

        print '! ~ ' * 22
        print "url: %s" % url
        try:
            resp = requests.get(url, headers=header, timeout=1)
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
                cityid = cityname = ''
                for k, v in weatherinfo.iteritems():
                    if not k or not v:
                        continue
                    if k == 'cityname':
                        cityname = v
                    elif k == 'city':
                        cityid = v
                    else:
                        pass
                else:
                    if cityid and cityname:
                        is_modal = self.citybo.get_modal_by_name(cityname)
                        if not is_modal:
                            modal = CityIdsModal()
                            modal.id = self.citybo.get_max_id() + 1
                            modal.cid = cityid
                            modal.cname = cityname
                            modal.ts = s2d(get_cur_time())
                            self.citybo.add(modal)
                            print 'add %s: %s' % (city_id, cityname)
                        else:
                            is_modal.cid = cityid
                            is_modal.cname = cityname
                            is_modal.ts = s2d(get_cur_time())
                            self.citybo.update(is_modal)
                            print 'update %s: %s' % (city_id, cityname)
        except Exception as e:

            print '* ' * 22
            print '_deal_city is error: %s' % e.message
            print '* ' * 22
            self.citybo.session.rollback()

        else:
            self.citybo.session.commit()


if __name__ == '__main__':
    city_src().run()
