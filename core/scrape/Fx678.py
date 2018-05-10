#coding=utf-8
import sys
import json
import datetime
import requests
import re
import traceback
import DataSource
from resource import Configuration

def deal_with_query():
    """ 汇通网数据抓取处理函数 """
    info_dict = {}
    ret_list = [] # 待返回的数据列表
    try:
        #数据请求
        r = requests.get(DataSource.FX678_XAG_URL,headers=DataSource.FX678_REQUEST_HEADER)
        if r.status_code != 200:
            return ret_list

        response_data = json.loads(r.text)
        close_price = str(response_data['c']).strip('[u\'\']')
        time_stamp = str(response_data['t']).strip('[u\'\']')
        #时间戳转datatime结构
        ret_list = [close_price,datetime.datetime.fromtimestamp(float(time_stamp))]
    except (Exception),e:
        exc_type,exc_value,exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
        traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))
    finally:
        return ret_list

