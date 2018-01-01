#coding=utf-8

import sqlite3
import os
import threading
import platform
from resource import Configuration
from resource import Constant
from resource import Primitive
from resource import Trace

class QuotationDB():
    """ 行情数据库类 """
    def __init__(self,flagList,recordDict):
        self.updatePeriodFlag = flagList
        self.recordPeriodDict = recordDict

    def create_period_db(self):
        """ 外部接口API: 创建数据库文件：行情数据库 """
        for tagPeriod in Constant.QUOTATION_DB_PREFIX[1:]:
            # 生成各周期时间数据库文件。心跳定时器的数据库文件冗余（忽略）。
            filePath = Configuration.get_period_working_folder(tagPeriod)+tagPeriod+'.db'
            isExist = os.path.exists(filePath)
            db = sqlite3.connect(filePath)
            dbCursor = db.cursor()
            #First: create db if empty
            if not isExist:
                try:
                    dbCursor.execute(Primitive.QUOTATION_DB_CREATE)
                except (Exception),e:
                    Trace.output('fatal',"create quotation db file Exception: "+e.message)
            db.commit()
            dbCursor.close()
            db.close()

    def insert_period_db_opera(self, dbFile, priceList):
        """ 内部接口API: 更新各周期行情数据库 """
        db = sqlite3.connect(dbFile)
        dbCursor = db.cursor()
        #First: file should be existed
        #Second: insert some information
        try:
            dbCursor.execute(Primitive.QUOTATION_DB_INSERT, priceList)
        except (Exception),e:
            Trace.output('fatal',"insert item to quotation db Exception: " + e.message)

        db.commit()
        dbCursor.close()
        db.close()

    def update_period_db(self, period):
        """ 外部接口API: 定时器回调函数--行情数据库更新。对各周期数据库进行更新。
            period:定时器线程字符串名称，亦即对应数据库文件名抬头
        """
        # 每日结算期间只需要更新一次相关数据库
        if self.updatePeriodFlag[Constant.QUOTATION_DB_PREFIX.index(period)] == True:
            return
        #组装对应数据库文件路径
        dbFile = Configuration.get_period_working_folder(period)+period+'.db'
        #挑取对应周期字典项
        priceDict = self.recordPeriodDict[period]
        #字典项转换成列表项
        priceList = [priceDict[Constant.QUOTATION_STRUCTURE[0]],\
                     priceDict[Constant.QUOTATION_STRUCTURE[1]],\
                     priceDict[Constant.QUOTATION_STRUCTURE[2]],\
                     priceDict[Constant.QUOTATION_STRUCTURE[3]],\
                     priceDict[Constant.QUOTATION_STRUCTURE[4]]]
        Trace.output('info','Period:%s '%period+'time out at %s '%priceList[0]+'open:%s'%priceList[1]+\
                     ' high:%s'%priceList[2]+' low:%s'%priceList[3]+' close:%s'%priceList[4])
        if priceList.count(0) != 0: # 若存在零值，则不插入数据库中。
            return
        self.insert_period_db_opera(dbFile, priceList)

        # 设置数据库更新标志
        self.updatePeriodFlag[Constant.QUOTATION_DB_PREFIX.index(period)] = True
        # 记录最小周期行情定时器到期
