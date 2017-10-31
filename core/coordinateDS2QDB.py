#coding=utf-8

import sys
from engine.DataScrape import *
from timer.TimerMotor import *
from database.QuotationDB import *
from database.QuotationRecord import *
from resource.Configuration import *
from resource.Constant import *
from resource.ExceptDeal import *

class coordinateDS2QDB():
    def __init__(self):
        self.dumpFlag = True

        self.cnstHdl = Constant()
        self.excptHdl = ExceptDeal()
        self.cnfHdl = Configuration()

        self.dtScrp = DataScrape() # 初始化数据抓取模块
        # Quotation record Handle
        self.recordHdl = QuotationRecord(self.cnfHdl.get_update_flag(),\
                                         self.cnfHdl.get_update_lock())
        # Quotation DB Handle
        self.dbQuotationHdl = QuotationDB(self.cnfHdl.get_update_flag(),\
                                          self.cnfHdl.get_update_lock(),\
                                          self.recordHdl.get_record_dict())

    def init_quotation(self):
        """ 外部接口API:行情数据库线程准备 """
        self.cnstHdl.get_version_info()
        # 创建记录字典
        self.recordHdl.create_record_dict()
        # 创建行情数据库文件
        self.dbQuotationHdl.create_period_db(self.cnfHdl.create_db_path())

    # 以下是定时器回调函数:
    def work_DS2QDB_heartbeat(self):
        """ 快速定时器(心跳定时器)回调函数 : 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数 """
        # 全球市场结算期间不更新缓冲记录
        if self.cnstHdl.is_closing_market():
            return
        if self.excptHdl.is_weekend():
            sys.exit()

        # 数据抓取并筛选
        infoList = self.dtScrp.query_info()
        if len(infoList) != 0:
            self.recordHdl.update_dict_record(infoList)

    def work_DS2QDB_operate(self):
        """ 慢速定时器组回调函数 : 更新行情数据库 """
        # 全球市场结算时间不更新数据库
        if self.cnstHdl.is_closing_market():
            return
        if self.excptHdl.is_weekend():
            sys.exit()

        self.dbQuotationHdl.update_period_db()
