#coding=utf-8

import datetime
import sqlite3
import re, os
QUOTATION_STRUCTURE = ['startPrice','realPrice','maxPrice','minPrice','time']
QUOTATION_DB_CREATE = '''create table quotation(
    id integer primary key autoincrement not null default 1,
    startPrice   float,
    realPrice    float,
    maxPrice     float,
    minPrice     float,
    time         float);'''

QUOTATION_DB_INSERT = 'insert into quotation (startPrice,realPrice,maxPrice,minPrice,time)\
    values(?, ?, ?, ?, ?)'

class QuotationDB():
    """"""
    def __init__(self):
        self.dumpFlag = True
        #快速定时器中缓冲字典.数据结构与QDB数据库每行相同.
        self.recordDict = {}

    def create_record_dict(self):
        """创建缓冲字典"""
        self.recordDict = dict(zip(QUOTATION_STRUCTURE,[0,0,0,0,'']))

    def update_record_dict(self,infoTuple):
        """快速定时器回调函数。更新缓冲字典--行情数据库二级缓冲中的第一级"""
        for i in list(infoTuple):
            #对于"startPrice"和"realPrice"项暂时不做处理.即只处理infoTuple中第三/四项.
            self.recordDict['startPrice'] = infoTuple[0]
            self.recordDict['realPrice'] = infoTuple[1]

            if(self.recordDict['maxPrice'] < infoTuple[2]):
                self.recordDict['maxPrice'] = infoTuple[2]
            if(self.recordDict['minPrice'] > infoTuple[3] or \
                           self.recordDict['minPrice'] == 0):
                self.recordDict['minPrice'] = infoTuple[3]

            self.recordDict['time'] = infoTuple[4]
        print "update record dict"

    def get_record(self):
        """获取缓冲字典中的内容.(转换成列表返回)"""
        return [self.recordDict['startPrice'],self.recordDict['realPrice'],self.recordDict['maxPrice'],\
                self.recordDict['minPrice'],self.recordDict['time']]

    def create_file(self):
        """ build database """
        dt = datetime.datetime.now()
        year,week = dt.strftime('%Y'),dt.strftime('%U')

        fileNamePrefix = folderName = year+'-'+week

        if not os.path.exists(folderName):
            # 创建当周数据库文件夹
            os.makedirs(folderName)

        file = fileNamePrefix+'/'+fileNamePrefix+'.db'
        isExist = os.path.exists(file)
        db = sqlite3.connect(file)
        dbCursor = db.cursor()
        #First: create db if empty
        if not isExist:
            try:
                dbCursor.execute(QUOTATION_DB_CREATE)
            except (Exception),e:
                print "create quotation db file Exception: "+e.message
        db.commit()
        dbCursor.close()
        db.close()

        return file

    def db_quotation_insert(self, file, priceList):
        """行情数据库插入操作"""
        db = sqlite3.connect(file)
        dbCursor = db.cursor()
        #First: file should be existed
        #Second: insert some information
        try:
            db.execute(QUOTATION_DB_INSERT,priceList)
        except (Exception),e:
            print "insert item to quotation db Exception: " + e.message

        db.commit()
        dbCursor.close()
        db.close()

    #def dbQuotationQuery