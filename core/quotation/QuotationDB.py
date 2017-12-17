#coding=utf-8

import sqlite3
import os
import threading
import platform
from copy import deepcopy

from resource import Constant
from resource import Primitive
from resource import Trace

class QuotationDB():
    """ 行情数据库类 """
    def __init__(self,workPath,flagList,recordDict):
        self.workPath = workPath
        self.updatePeriodFlag = flagList
        self.recordPeriodDict = recordDict

    def create_period_db(self):
        """ 外部接口API: 创建数据库文件：行情数据库 (ER数据库可仿效) """
        for tagPeriod in list(Constant.QUOTATION_DB_PREFIX):
            # 生成各周期时间数据库文件。10sec.db数据库文件冗余（忽略）。
            isExist = os.path.exists(self.workPath + tagPeriod+'.db')
            db = sqlite3.connect(self.workPath + tagPeriod+'.db')
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

    def update_period_db(self, index):
        """ 外部接口API: 定时器回调函数--行情数据库更新。对各周期数据库进行更新。
            index:根据定时器线程名称中的编号找到对应数据库文件
        """
        #组装对应数据库文件路径
        dbFile = self.workPath+Constant.QUOTATION_DB_PREFIX[index]+'.db'
        #挑取对应周期字典项
        priceDict = self.recordPeriodDict[Constant.QUOTATION_DB_PREFIX[index]]
        #字典项转换成列表项
        priceList = [priceDict[Constant.QUOTATION_STRUCTURE[0]],\
                     priceDict[Constant.QUOTATION_STRUCTURE[1]],\
                     priceDict[Constant.QUOTATION_STRUCTURE[2]],\
                     priceDict[Constant.QUOTATION_STRUCTURE[3]],\
                     priceDict[Constant.QUOTATION_STRUCTURE[4]]]
        Trace.output('info','Period:%s '%Constant.QUOTATION_DB_PREFIX[index]+\
                     'time out at %s '%priceList[0]+'open:%s'%priceList[1]+\
                     ' high:%s'%priceList[2]+' low:%s'%priceList[3]+' close:%s'%priceList[4])
        self.insert_period_db_opera(dbFile, priceList)

        # 设置数据库更新标志
        self.updatePeriodFlag[index] = True
        # 记录最小周期行情定时器到期
