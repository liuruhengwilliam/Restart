#coding=utf-8

import sys
import DataSource
import Fx678
import EastMoney
from resource import ExceptDeal
from resource import Trace
from resource import Property

class DataScrape():
    """ 数据抓取类 """
    def __init__(self):
        self.dumpFlag = True

    def query_info(self):
        """ 外部接口API：获取某网站相关信息 """
        urlName = ''
        #每个数据源采集的字典结构可能(基本都)会不同，但是统一返回两项值：当前价格和当前时间。
        retList = [None,None]
        dataSrc = [Property.get_property("datasource")] + map(lambda x:x,DataSource.URL_SRC_TUPLE)

        for urlName in dataSrc:
            if urlName == 'Fx678':#高优先级排前
                retList = Fx678.deal_with_query()
            elif urlName == 'EastMoney':#低优先级排后
                retList = EastMoney.deal_with_query()
            elif urlName is None:
                continue

            if retList[0] != None and retList[1] != None:
                break
            else:
                Trace.output('warn','Data Source:'+urlName+' get price('+retList[0]+') failed on '+retList[1]+'!')

        else:# 若从以上数据源都未获取有效数据就引发自定义异常
            try:
                raise ExceptDeal.engineException()
            except ExceptDeal.engineException as e:
                Trace.output('fatal',"query info error on DataScrape module!")
                pass

        if self.dumpFlag:
            Trace.output('info',urlName+' '+' '.join(retList))
        return retList

