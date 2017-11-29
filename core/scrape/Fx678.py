#coding=utf-8
import sys
import datetime
import requests
import re
import traceback
import DataSource

def deal_with_query():
    """ 汇通网数据抓取处理函数 """
    info_dict = {}
    ret_list = [] # 待返回的数据列表
    try:
        #数据请求
        r = requests.get(DataSource.FX678_XAG_URL)
        #数据进行切片分割
        content = r.text.split('{')[1].split('}')[0].split(',')
        #print content
        tag =[]
        value = []

        for item in content:
            tag.append(item.split(':')[0])
            value.append(item.split(':')[1].strip('[""]'))
            #转化成字典格式保存
            info_dict = dict(zip(tag,value))

        #print info_dict
        # 用"最新价( b )"刷新各周期数据库
        #ret_list = [infoDict[u'"p"'],infoDict[u'"b"'],infoDict[u'"h"'],infoDict[u'"l"'],\
        ret_list = [info_dict[u'"b"'],datetime.datetime.fromtimestamp(float(info_dict[u'"t"']))]
    except (Exception),e:
        exc_type,exc_value,exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
    finally:
        return ret_list

