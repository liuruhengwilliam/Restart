#coding=utf-8

import datetime
import sqlite3
import re, os
import platform
import threading
from copy import deepcopy
from resource import Configuration
from resource import Primitive

class QuotationDB():
    """ 行情数据库类 """
    def __init__(self):
        # 调试打印开关
        self.dumpFlag = True
        # 结算期间标志
        self.isClosingQuotation = False
        # 数据库文件路径及文件名
        self.fileQDBPath = None

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
        """ 外部接口API: 心跳定时器回调函数。更新缓冲字典和周期字典。 """
        # 全球市场结算期间不更新缓冲字典
        if self.recordPeriodDict['10sec']['time'] == infoTuple[4]:
            self.isClosingQuotation = True
            return
        else:
            self.isClosingQuotation = False

        tmName = threading.currentThread().getName()
        index = (tmName.split('-'))[1]

        for i in range(len(Configuration.QUOTATION_DB_PERIOD)):
            dictItem = self.recordPeriodDict[Configuration.QUOTATION_DB_PREFIX[i]]
            self.updateLock[i].acquire()
            #每次行情数据库更新后且各周期定时器首次到期时"startPrice"应该等于"realPrice"项，并且不再后续不更新。
            #对于'10sec'定时器，忽略该设置。
            if self.updatePeriodFlag[i] == True:
                dictItem['startPrice'] = infoTuple[1]
                self.updatePeriodFlag[i] = False
            self.updateLock[i].release()

            dictItem['realPrice'] = infoTuple[1]

            if(dictItem['maxPrice'] < infoTuple[2]):
                dictItem['maxPrice'] = infoTuple[2]
            if(dictItem['minPrice'] > infoTuple[3] or dictItem['minPrice'] == 0):
                dictItem['minPrice'] = infoTuple[3]

            dictItem['time'] = infoTuple[4]

    def create_period_db_path(self):
        """ 内部接口API: 生成文件名及文件路径 """
        # 寻找当前周数并生成文件名前缀
        dt = datetime.datetime.now()
        year,week = dt.strftime('%Y'),dt.strftime('%U')
        fileNamePrefix = year+'-'+week

        #生成文件路径(依据不同操作系统)
        sysName = platform.system()
        if (sysName == "Windows"):
            self.fileQDBPath = 'D:/mess/future/'+fileNamePrefix
        elif (sysName == "Linux"):
            self.fileQDBPath = '~/mess/future/'+fileNamePrefix
        else :# 未知操作系统
            self.fileQDBPath = fileNamePrefix

        if not os.path.exists(self.fileQDBPath):
            # 创建当周数据库文件夹
            os.makedirs(self.fileQDBPath)

    def create_period_db_file(self):
        """ 外部接口API: 创建数据库文件：行情数据库 (ER数据库可仿效) """
        self.create_period_db_path()
        for tagPeriod in list(Configuration.QUOTATION_DB_PREFIX):
            # 生成各周期时间数据库文件。10sec.db数据库文件冗余（忽略）。
            isExist = os.path.exists(self.fileQDBPath+'/'+tagPeriod+'.db')
            db = sqlite3.connect(self.fileQDBPath+'/'+tagPeriod+'.db')
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
        # 全球市场结算时间不更新数据库
        if self.isClosingQuotation == True:
            return
        #根据定时器线程名称中的编号找到对应数据库文件
        dbName = threading.currentThread().getName()
        index = int((dbName.split('-'))[1]) - 1
        #组装对应数据库文件路径
        dbFile = self.fileQDBPath+'/'+Configuration.QUOTATION_DB_PREFIX[index]+'.db'
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



