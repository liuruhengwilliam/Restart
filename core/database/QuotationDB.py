#coding=utf-8

import sqlite3
import os
import threading
from copy import deepcopy
from resource import Configuration
from resource import Primitive

class QuotationDB():
    """ 行情数据库类 """
    def __init__(self):
        # 调试打印开关
        self.dumpFlag = True
        self.filePath = None
        # 开盘和收盘记录的更新标志位。快速定时器和慢速定时器竞争资源，需要锁机制进行保护。
        self.updatePeriodFlag = [True]*len(Configuration.QUOTATION_DB_PERIOD)
        # 锁资源。与定时器数目对应。
        self.updateLock = [threading.RLock()]*len(Configuration.QUOTATION_DB_PERIOD)

        # QDB中各周期记录字典
        self.recordPeriodDict = {}

    # 用列表还是用字典？ 字典可读性优于列表，后期维护性较高。-- 字典'键值对'本身就是一种注释。
    def create_record_dict(self):
        """ 外部接口API: 创建记录字典:缓冲记录字典 和 周期记录字典 """
        atomicDictItem = dict(zip(Configuration.QUOTATION_STRUCTURE,[0,0,0,0,'']))

        # 生成各周期记录字典
        for tagPeriod in list(Configuration.QUOTATION_DB_PREFIX):
            itemPeriod = {tagPeriod: deepcopy(atomicDictItem)}
            self.recordPeriodDict.update(itemPeriod)

    def update_dict_record(self,infoTuple):
        """ 外部接口API: 心跳定时器回调函数。更新缓冲记录。 """

        #用最快定时器（心跳定时器）来更新其他周期行情数据记录
        for i in range(len(Configuration.QUOTATION_DB_PERIOD)):
            dictItem = self.recordPeriodDict[Configuration.QUOTATION_DB_PREFIX[i]]
            dictItem['time'] = infoTuple[4]

            self.updateLock[i].acquire()
            #每次行情数据库更新后各周期定时器首次到期时，开盘价/最高/最低都等于实时价格，且开盘价后续不更新。
            #对于最快定时器（暂定10秒），忽略该设置。
            if self.updatePeriodFlag[i] == True:
                dictItem['startPrice'] = dictItem['realPrice'] = \
                    dictItem['maxPrice'] = dictItem['minPrice'] = infoTuple[1]
                self.updatePeriodFlag[i] = False
                self.updateLock[i].release()
                continue
            else:
                dictItem['realPrice'] = infoTuple[1]
            self.updateLock[i].release()

            #实时价格和最高/最低价格进行比较。bug fix only for FX678URL source. 2017-10-25
            if(dictItem['maxPrice'] < infoTuple[1]):
                dictItem['maxPrice'] = infoTuple[1]
            elif(dictItem['minPrice'] > infoTuple[1]):
                dictItem['minPrice'] = infoTuple[1]

    def create_period_db_file(self, filePath):
        """ 外部接口API: 创建数据库文件：行情数据库 (ER数据库可仿效) """
        self.filePath = filePath
        for tagPeriod in list(Configuration.QUOTATION_DB_PREFIX):
            # 生成各周期时间数据库文件。10sec.db数据库文件冗余（忽略）。
            isExist = os.path.exists(filePath+'/'+tagPeriod+'.db')
            db = sqlite3.connect(filePath+'/'+tagPeriod+'.db')
            dbCursor = db.cursor()
            #First: create db if empty
            if not isExist:
                try:
                    dbCursor.execute(Primitive.QUOTATION_DB_CREATE)
                except (Exception),e:
                    print "create quotation db file Exception: "+e.message
            db.commit()
            dbCursor.close()
            db.close()

    def insert_period_db_opera(self, dbFilePath, priceList):
        """ 内部接口API: 更新各周期行情数据库 """
        db = sqlite3.connect(dbFilePath)
        dbCursor = db.cursor()
        #First: file should be existed
        #Second: insert some information
        try:
            db.execute(Primitive.QUOTATION_DB_INSERT, priceList)
        except (Exception),e:
            print "insert item to quotation db Exception: " + e.message

        db.commit()
        dbCursor.close()
        db.close()

    def update_period_db(self):
        """ 外部接口API: 定时器回调函数--行情数据库更新。对各周期数据库进行更新。"""

        #根据定时器线程名称中的编号找到对应数据库文件
        dbName = threading.currentThread().getName()
        index = int((dbName.split('-'))[1]) - 1
        #组装对应数据库文件路径
        dbFile = self.filePath+'/'+Configuration.QUOTATION_DB_PREFIX[index]+'.db'
        #挑取对应周期字典项
        priceDict = self.recordPeriodDict[Configuration.QUOTATION_DB_PREFIX[index]]
        #字典项转换成列表项
        priceList = [priceDict['startPrice'],priceDict['realPrice'],priceDict['maxPrice'],\
                     priceDict['minPrice'],priceDict['time']]
        self.insert_period_db_opera(dbFile, priceList)

        # 设置数据库更新标志
        self.updateLock[index].acquire()
        self.updatePeriodFlag[index] = True
        # 记录最小周期行情定时器到期
        self.updateLock[index].release()



