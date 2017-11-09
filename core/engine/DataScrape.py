#coding=utf-8

import sys
import DataSource
from resource import ExceptDeal
import Fx678
import EastMoney

class DataScrape():
    """ 数据抓取类 """
    def __init__(self):
        self.dumpFlag = True

    def query_info(self):
        """ 外部接口API：获取某网站相关信息 """
        #每个数据源采集的字典结构可能(基本都)会不同，但是统一返回两项值：当前价格和当前时间。
        ret_list = [None,None]
        for url_item in DataSource.URL_SRC_ENUM:
            if url_item == 'Fx678':#第一优先级
                ret_list = Fx678.deal_with_query()
            elif url_item == 'EastMoney':
                ret_list = EastMoney.deal_with_query()

            if ret_list[0] != None and ret_list[1] != None: break

        else:# 若从以上数据源都未获取有效数据就引发自定义异常
            try:
                raise ExceptDeal.engineException()
            except ExceptDeal.engineException as e:
                print "query info error on DataScrape module!"
                sys.exit()

        if self.dumpFlag: print ret_list
        return ret_list

