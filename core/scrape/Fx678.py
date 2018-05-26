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
    """ 汇通网数据抓取处理函数
        返回值：列表结构---浮点型实时价格，时间字符串
    """
    ret_list = [] # 待返回的数据列表
    try:
        #数据请求
        r = requests.get(DataSource.FX678_XAG_URL,headers=DataSource.FX678_REQUEST_HEADER)
        if r.status_code != 200:
            return ret_list

        response_data = json.loads(r.text)
        close_price = str(response_data['c']).strip('[u\'\']')
        #time_stamp = str(response_data['t']).strip('[u\'\']')
        #时间戳转datatime结构
        #stampDt = datetime.datetime.fromtimestamp(float(time_stamp))
        # 为减少后续异常逻辑分支的处理，用当前PC时间取代网络时间戳
        ret_list = [float(close_price),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    except (Exception),e:
        exc_type,exc_value,exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
        traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))
    finally:
        return ret_list

