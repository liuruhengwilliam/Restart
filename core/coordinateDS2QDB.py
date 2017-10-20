#coding=utf-8

import sys
from engine.DataScrape import *
from timer.TimerMotor import *
from database.QuotationDB import *

class coordinateDS2QDB():
    def __init__(self):
        self.dumpFlag = True

    def init_data_scrape(self):
        self.dtScrp = DataScrape()
        self.infoTuple = None#数据筛选后列表（待缓冲字典处理）

    def init_quotation_db(self):
        """ 行情数据库线程准备 """
        # 创建线程
        self.event = threading.Event()

        # 对应数据库准备
        self.dbQuotationDBHdl = QuotationDB()#Quotation DB Handle
        #创建缓冲记录字典
        self.dbQuotationDBHdl.create_record_dict()
        #Quotation DB file name(with path)
        self.dbQuotationDBHdl.create_file()

    # 以下是定时器回调函数:
    def work_QDB_update(self):
        """ 慢速定时器回调函数 : 更新行情数据库 """
        self.dbQuotationDBHdl.insert_record()

    def work_DS2QDB_record(self):
        """ 快速定时器回调函数 : 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数 """
        #数据抓取并筛选
        self.infoTuple = self.dtScrp.query_info()
        if self.dumpFlag: print self.infoTuple
        self.dbQuotationDBHdl.update_record_dict(self.infoTuple)

    def idiot(self):
        print "idiot"