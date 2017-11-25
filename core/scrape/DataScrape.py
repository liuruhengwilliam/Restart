#coding=utf-8

import sys
import DataSource
import Fx678
import EastMoney
from resource import ExceptDeal
from resource import Trace
from resource import Configuration

class DataScrape():
    """ 数据抓取类 """

    def query_info(self):
        """ 外部接口API：获取某网站相关信息 """
        urlName = ''
        #每个数据源采集的字典结构可能(基本都)会不同，但是统一返回两项值：当前价格和当前时间。
        retList = []
        dataSrc = Configuration.get_property("datasource")

        #非法数据源就直接返回
        if DataSource.URL_SRC_TUPLE.count(dataSrc) == 0:
            return retList

        if dataSrc == 'Fx678':#高优先级排前
            retList = Fx678.deal_with_query()
        elif dataSrc == 'EastMoney':#低优先级排后
            retList = EastMoney.deal_with_query()
        else:
            return retList

        if len(retList) == 2 and retList[0] != '' and retList[1] != '':
            Trace.output('info',dataSrc+' '+' '.join(retList))
        else:# 若从以上数据源都未获取有效数据就引发自定义异常
            Trace.output('warn','Data Source:'+dataSrc+' get price failed!')
            try:
                raise ExceptDeal.engineException()
            except ExceptDeal.engineException as e:
                Trace.output('fatal',"query info error on DataScrape module!")
                pass

        return retList

