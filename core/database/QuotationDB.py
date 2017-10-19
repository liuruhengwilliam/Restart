#coding=utf-8

import datetime
import sqlite3
import re, os

QUOTATION_STRUCTURE = ('startPrice','realPrice','maxPrice','minPrice','time')

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