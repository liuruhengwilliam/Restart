#coding=utf-8

import sys
import DataSource
import Fx678
import EastMoney
from resource import ExceptDeal
from resource import Trace

class DataScrape():
    """ 数据抓取类 """
    def __init__(self):
        self.dumpFlag = True

    def query_info(self):
        """ 外部接口API：获取某网站相关信息 """
        urlName = ''
        #每个数据源采集的字典结构可能(基本都)会不同，但是统一返回两项值：当前价格和当前时间。
        retList = [None,None]
        for urlName in DataSource.URL_SRC_ENUM:
            if urlName == 'Fx678':#第一优先级
                retList = Fx678.deal_with_query()
            elif urlName == 'EastMoney':
                retList = EastMoney.deal_with_query()

            if retList[0] != None and retList[1] != None: break

        else:# 若从以上数据源都未获取有效数据就引发自定义异常
            try:
                raise ExceptDeal.engineException()
            except ExceptDeal.engineException as e:
                Trace.output('fatal',"query info error on DataScrape module!")
                pass

        if self.dumpFlag:
            Trace.output('info',urlName+' '+' '.join(retList))
        return retList

