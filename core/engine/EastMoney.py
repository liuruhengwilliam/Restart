#coding=utf-8
import sys
import time
import requests
import re
import traceback
import DataSource

def deal_with_query():
    """ 东方财富网数据抓取处理函数 """
    ret_list = [] # 待返回的数据列表
    ret_price = None
    ret_timestamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

    time_tick_beijin = (int(time.time()))*1000

    eastmoney_url = DataSource.EASTMONEY_URL_FRAGMENT1+DataSource.EASTMONEY_URLUNKNOW_TIMESTAMP+\
        str(time_tick_beijin)+DataSource.EASTMONEY_URL_FRAGMENT2

    try:
        #数据请求
        r = requests.get(eastmoney_url)
        #数据进行切片分割
        info_content = r.text.split('(')[1].split(')')[0]
        #print info_content
        for item in (info_content.split('%"')):
            if item.strip(',').strip('[').find('XAG') != -1:
                #print item.strip(',').strip('[').split(',')
                if len(item.strip(',').strip('[').split(',')) > 3:
                    ret_price = item.strip(',').strip('[').split(',')[3]
                break
        ret_list = [ret_price,ret_timestamp]
    except (Exception),e:
        exc_type,exc_value,exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
    finally:
        return ret_list
