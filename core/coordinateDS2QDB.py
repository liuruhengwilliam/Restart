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
        self.infoTuple = None#数据筛选后列表（待插入行情数据库）

    def init_quotation_db(self):
        """ 行情数据库线程准备 """
        # 创建线程
        self.event = threading.Event()
        self.thrdQuotaionDB = threading.Thread()
        # 对应数据库准备
        self.dbQuotationDBHdl = QuotationDB()#Quotation DB Handle
        #Quotation DB file name(with path)
        self.dbQuotationFile = self.dbQuotationDBHdl.create_file()

        #行情数据库线程挂载回调函数并等待event消息驱动
        thrdQuotationDB = threading.Thread(target=self.thrd_quotation_db_func)
        #行情数据库线程启动
        thrdQuotationDB.start()

    def get_quotation_db_hdl(self):
        return self.dbQuotationDBHdl

    def get_quotation_db_file(self):
        return self.dbQuotationFile

    def thrd_quotation_db_func(self):
        """行情数据库线程主函数"""
        while True:
            self.event.wait()
            #if self.event.isSet():
            self.dbQuotationDBHdl.db_quotation_insert(self.dbQuotationFile, self.infoTuple)
            self.event.clear()

    def work_DS2Quotaion(self):
        """ 数据抓取模块和行情数据库线程之间协同工作函数（定时器线程回调函数） """
        #数据抓取并筛选
        self.infoTuple = self.dtScrp.query_info()
        if self.dumpFlag: print self.infoTuple
        #消息通知行情数据库操作
        self.event.set()

    def idiot(self):
        print "idiot"