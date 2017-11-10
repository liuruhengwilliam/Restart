#coding=utf-8

import sys
import datetime

from resource import Configuration
from resource import Constant
from resource import ExceptDeal
from engine.DataScrape import *
from timer.TimerMotor import *

from quotation.QuotationDB import *
from quotation.QuotationRecord import *

class coordinateDS2QDB():
    def __init__(self):
        self.dumpFlag = True
        self.week = (datetime.datetime.now()).strftime('%U')# 本周周数记录

        self.dtScrp = DataScrape() # 初始化数据抓取模块
        # Quotation record Handle
        self.recordHdl = QuotationRecord(Configuration.UPDATE_PERIOD_FLAG,\
                                         Configuration.UPDATE_LOCK)
        # Quotation DB Handle
        self.dbQuotationHdl = QuotationDB(Configuration.UPDATE_PERIOD_FLAG,\
                                          Configuration.UPDATE_LOCK,\
                                          self.recordHdl.get_record_dict())

    def init_quotation(self):
        """ 外部接口API:行情数据库线程准备 """
        Constant.get_version_info()
        # 创建记录字典
        self.recordHdl.create_record_dict()
        # 创建行情数据库文件
        self.dbQuotationHdl.create_period_db(Configuration.get_working_directory())

    # 以下是定时器回调函数:
    def work_DS2QDB_heartbeat(self):
        """ 快速定时器(心跳定时器)回调函数 : 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数 """
        # 全球市场结算期间不更新缓冲记录
        if Constant.is_closing_market():
            return
        if ExceptDeal.exit_on_weekend(self.week):
            sys.exit()

        # 数据抓取并筛选
        infoList = self.dtScrp.query_info()
        if len(infoList) != 0:
            self.recordHdl.update_dict_record(infoList)

    def work_DS2QDB_operate(self):
        """ 慢速定时器组回调函数 : 更新行情数据库 """
        # 全球市场结算时间不更新数据库
        if Constant.is_closing_market():
            return
        if ExceptDeal.exit_on_weekend(self.week):
            sys.exit()

        self.dbQuotationHdl.update_period_db()
