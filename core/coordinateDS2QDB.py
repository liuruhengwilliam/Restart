#coding=utf-8

import sys
import threading
from engine.DataScrape import *
from timer.TimerMotor import *
from database.QuotationDB import *

class coordinateDS2QDB():
    def __init__(self):
        self.dumpFlag = True

    def init_data_scrape(self):
        self.dtScrp = DataScrape()
        self.infoTuple = None#数据筛选后列表（待缓冲字典处理）
        self.recordTuple = None#缓冲记录后列表（待插入行情数据库）

    def init_quotation_db(self):
        """ 行情数据库线程准备 """
        # 创建线程
        self.event = threading.Event()
        self.thrdQuotaionDB = threading.Thread()
        # 对应数据库准备
        self.dbQuotationDBHdl = QuotationDB()#Quotation DB Handle
        #创建缓冲记录字典
        self.dbQuotationDBHdl.create_record_dict()
        #Quotation DB file name(with path)
        self.dbQuotationFile = self.dbQuotationDBHdl.create_file()

        #行情数据库线程挂载回调函数并等待event消息驱动
        thrdQuotationDB = threading.Thread(target=self.thrd_quotation_db_func)
        #行情数据库线程启动
        thrdQuotationDB.start()

    def thrd_quotation_db_func(self):
        """行情数据库线程主函数"""
        while True:
            self.event.wait()
            #if self.event.isSet():
            self.dbQuotationDBHdl.db_quotation_insert(self.dbQuotationFile, self.recordTuple)
            self.event.clear()

    def work_DS2QDB_record(self):
        """ 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数（快速定时器线程回调函数） """
        #数据抓取并筛选
        self.infoTuple = self.dtScrp.query_info()
        if self.dumpFlag: print self.infoTuple
        self.dbQuotationDBHdl.update_record_dict(self.infoTuple)

    def work_QDB_update(self):
        """行情数据库更新(慢速定时器回调函数)"""
        self.recordTuple = self.dbQuotationDBHdl.get_record()
        if self.dumpFlag: print self.recordTuple
        #消息通知行情数据库操作
        self.event.set()

    def idiot(self):
        print "idiot"