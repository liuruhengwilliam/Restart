#coding=utf-8

import sys
import threading
from engine.DataScrape import *
from timer.TimerMotor import *
from database.QuotationDB import *

class core():
    def initDataScrape(self):
        self.dtScrp = DataScrape()
        self.infoTuple = None#数据筛选后列表（待插入行情数据库）

    def initQuotationDB(self):
        """ 行情数据库线程准备 """
        # 创建线程
        self.event = threading.Event()
        self.thrdQuotaionDB = threading.Thread()
        # 对应数据库准备
        self.dbQuotationDBHdl = QuotationDB()#Quotation DB Handle
        #Quotation DB file name(with path)
        self.dbQuotationFile = self.dbQuotationDBHdl.createFile()

        #挂载线程主处理函数并启动线程（等待消息）
        th = threading.Thread(target=self.thrdQuotationDBFunc)
        th.start()

    def getQuotationDBHdl(self):
        return self.dbQuotationHdl

    def getQuotationDBFile(self):
        return self.dbQuotationFile

    def thrdQuotationDBFunc(self):
        """行情数据库线程主函数"""
        self.event.wait()
        self.dbQuotationHdl.dbQuotationInsert(self.dbQuotationFile,self.infoTuple)

    def workDS2Quotaion(self):
        """ 数据抓取模块和行情数据库线程之间协同工作函数（定时器线程回调函数） """
        #数据抓取并筛选
        self.infoTuple = self.dtScrp.queryInfo()
        #消息通知行情数据库操作
        self.event.set()

