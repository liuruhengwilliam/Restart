#coding=utf-8

import sys
import datetime

from resource import Configuration
from resource import Constant
from resource import ExceptDeal
from scrape.DataScrape import *

from quotation.QuotationDB import *
from quotation.QuotationRecord import *

class Coordinate():
    """
        协作类:衔接“数据抓取”、“行情数据库”、“策略算法”模块，协同工作。
    """
    def __init__(self):
        self.week = (datetime.datetime.now()).strftime('%U')# 本周周数记录

        self.dtScrp = DataScrape() # 初始化数据抓取模块
        # Quotation record Handle
        self.recordHdl = QuotationRecord(Constant.UPDATE_PERIOD_FLAG,\
                                         Constant.UPDATE_LOCK)
        # Quotation DB Handle
        self.dbQuotationHdl = QuotationDB(Constant.UPDATE_PERIOD_FLAG,\
                                          Constant.UPDATE_LOCK,\
                                          self.recordHdl.get_record_dict())

    def init_quotation(self):
        """ 外部接口API:行情数据库准备 """
        # 创建记录字典
        self.recordHdl.create_record_dict()
        # 创建行情数据库文件
        self.dbQuotationHdl.create_period_db(Configuration.get_working_directory())

    def init_earnrate(self):
        """ 外部接口API：初始化胜率数据库 """

    # 以下是定时器回调函数:
    def work_heartbeat(self):
        """ 快速定时器(心跳定时器)回调函数 : 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数 """
        # 全球市场结算期间不更新缓冲记录
        if Constant.is_closing_market():
            return
        if Constant.exit_on_weekend(self.week):
            sys.exit()

        # 数据抓取并筛选
        infoList = self.dtScrp.query_info()
        if len(infoList) != 0:
            self.recordHdl.update_dict_record(infoList)

    def work_operation(self):
        """ 慢速定时器组回调函数 : 更新行情数据库和策略算法计算 """
        # 全球市场结算时间不更新数据库
        if Constant.is_closing_market():
            return
        if Constant.exit_on_weekend(self.week):
            sys.exit()

        self.dbQuotationHdl.update_period_db()

        # 各周期定时器到期之后，可根据需求调用策略算法模块的接口API对本周期数据进行计算。
