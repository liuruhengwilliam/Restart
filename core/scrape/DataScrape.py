#coding=utf-8

import sys
import DataSource
import Fx678
import SinaFinance
from resource import ExceptDeal
from resource import Trace
from resource import Configuration

def query_info():
    """ 外部接口API：获取某网站相关信息 """
    urlName = ''
    #每个数据源采集的字典结构可能(基本都)会不同，但是统一返回两项值：当前价格和当前时间。
    retList = []
    dataSrc = Configuration.get_property("datasource")

    #非法数据源就直接返回
    if DataSource.URL_SRC_TUPLE.count(dataSrc) == 0:
        dataSrc = DataSource.URL_SRC_DEFAULT

    if dataSrc == 'Fx678':#高优先级排前
        retList = Fx678.deal_with_query()
    elif dataSrc == 'SinaFinance':#低优先级排后
        retList = SinaFinance.deal_with_query()
    else:
        return retList

    if len(retList) == 2 and retList[0] != '' and retList[1] != '':
        None#Trace.output('info', dataSrc+'  %s '%retList[0]+retList[1].strftime('%c'))
    else:# 若从以上数据源都未获取有效数据就引发自定义异常
        Trace.output('warn','Data Source:'+dataSrc+' get price failed!')
        try:
            raise ExceptDeal.engineException()
        except ExceptDeal.engineException as e:
            Trace.output('fatal',"query info error on DataScrape module!")
            pass

    return retList

