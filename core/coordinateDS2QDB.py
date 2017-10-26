#coding=utf-8

import sys
from engine.DataScrape import *
from timer.TimerMotor import *
from database.QuotationDB import *
from resource.Configuration import *
from resource.Constant import *

class coordinateDS2QDB():
    def __init__(self):
        self.dumpFlag = True
        self.dtScrp = None
        self.dbQuotationDBHdl = None
        self.cnstHdl = Constant()
        self.cnfHdl = Configuration()

    def init_data_scrape(self):
        """ 初始化数据抓取模块 """
        self.dtScrp = DataScrape()

    def init_quotation_db(self):
        """ 行情数据库线程准备 """
        # 对应数据库准备
        self.dbQuotationDBHdl = QuotationDB() # Quotation DB Handle
        # 创建记录字典
        self.dbQuotationDBHdl.create_record_dict()
        # 创建行情数据库文件
        self.dbQuotationDBHdl.create_period_db_file(self.cnfHdl.create_db_path())

    # 以下是定时器回调函数:
    def work_DS2QDB_heartbeat(self):
        """ 快速定时器(心跳定时器)回调函数 : 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数 """
        # 全球市场结算期间不更新缓冲记录
        if self.cnstHdl.is_closing_market():
            return
        # 数据抓取并筛选
        infoList = self.dtScrp.query_info()
        if len(infoList) != 0:
            self.dbQuotationDBHdl.update_dict_record(infoList)

    def work_DS2QDB_operate(self):
        """ 慢速定时器组回调函数 : 更新行情数据库 """
        # 全球市场结算时间不更新数据库
        if self.cnstHdl.is_closing_market():
            print "closing market!"
            return

        self.dbQuotationDBHdl.update_period_db()
