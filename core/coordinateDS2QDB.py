#coding=utf-8

import sys
from engine.DataScrape import *
from timer.TimerMotor import *
from database.QuotationDB import *
from resource.Configuration import *

class coordinateDS2QDB():
    def __init__(self):
        self.dumpFlag = True
        self.dtScrp = None
        self.dbQuotationDBHdl = None
        self.cnfHdl = None

    def init_data_scrape(self):
        """ 初始化数据抓取模块 """
        self.dtScrp = DataScrape()

    def init_quotation_db(self):
        """ 行情数据库线程准备 """
        # 对应数据库准备
        self.cnfHdl = Configuration()

        self.dbQuotationDBHdl = QuotationDB() # Quotation DB Handle
        # 创建记录字典
        self.dbQuotationDBHdl.create_record_dict()
        # 创建行情数据库文件
        self.dbQuotationDBHdl.create_period_db_file(self.cnfHdl.create_db_path())

    # 以下是定时器回调函数:
    def work_DS2QDB_heartbeat(self):
        """ 快速定时器(心跳定时器)回调函数 : 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数 """
        # 数据抓取并筛选
        infoTuple = self.dtScrp.query_info()
        if self.dumpFlag: print infoTuple
        self.dbQuotationDBHdl.update_dict_record(infoTuple)

    def work_DS2QDB_operate(self):
        """ 慢速定时器组回调函数 : 更新行情数据库 """
        self.dbQuotationDBHdl.update_period_db()
