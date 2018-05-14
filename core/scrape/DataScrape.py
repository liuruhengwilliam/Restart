#coding=utf-8

import sys
import DataSource
import Fx678
import SinaFinance
from resource import Trace
from resource import Configuration

def query_info():
    """ 外部接口API：获取某网站相关信息 """
    #每个数据源采集的字典结构可能(基本都)会不同，但是统一返回两项值：当前价格(字符串结构)和当前时间(DateFrame结构)。

    for dataSrc in DataSource.URL_SRC_TUPLE:
        retList = []
        if dataSrc == 'Fx678':#高优先级排前
            retList = Fx678.deal_with_query()
        else:#低优先级排后
            retList = SinaFinance.deal_with_query()
        if len(retList) == 2:
            Trace.output('debug',"From %s, quote the price of %s at %s"\
                         %(dataSrc,retList[0],retList[1].strftime("%Y-%m-%d %H:%M:%S")))
            break
    else:
        Trace.output('fatal',"Failed to query price on DataScrape module from ALL OF DATASOURCE!")

    return retList

