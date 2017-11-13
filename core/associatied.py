#coding=utf-8

import re
import os
import sys
import csv
import sqlite3
import time
import datetime
import threading
import talib
import numpy
import requests
from engine.DataScrape import *
from timer.TimerMotor import *
from quotation.QuotationDB import *
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from resource import Primitive

event = threading.Event()
QUOTATION_DB_PREFIX = ['5min','15min','30min','1hour','2hour','4hour','6hour','12hour','1day','1week']
QUOTATION_DB_PERIOD = [5*60,15*60,30*60,1*3600,2*3600,4*3600,6*3600,12*3600,1*24*3600,5*24*3600]
QUOTATION_STRUCTURE = ['startPrice','realPrice','maxPrice','minPrice','time']

QUERY_ALL_SQL = 'select * from quotation'
QUERY_ID_SQL = 'select id from quotation'

#%matplotlib inline

def func():
    # 等待事件，进入等待阻塞状态
    print '%s wait for event...' % threading.currentThread().getName()
    event.wait()

    # 收到事件后进入运行状态
    print '%s recv event.' % threading.currentThread().getName()

def csv_test(priceList):
    csvFile = 'D:/misc/future/2017-44/5min.csv'
    #挑取对应周期字典项
    csvFile = file(csvFile, 'wb')
    csvWriter = csv.writer(csvFile, dialect='excel')
    for item in priceList:
        csvWriter.writerow(item)
    csvFile.close()

def file_test():
    for line in open('D:/misc/future/2017-44/5min.db'):
        print line

def db_test():
    dbFile = 'D:/misc/future/2017-44/5min.db'
    db = sqlite3.connect(dbFile)
    dbCursor = db.cursor()
    try:
        #results = dbCursor.execute(QUERY_ALL_SQL)
        results = dbCursor.execute(Primitive.QUOTATION_DB_QUERY_DESC)
        #ret = results.fetchall()
        ret = results.fetchmany(1)
    except (Exception),e:
        print "query in quotation db Exception: " + e.message
    db.commit()
    dbCursor.close()
    db.close()
    print ret
    return ret

def datetime_test():
    dt = datetime.datetime.now()
    #print str(int(dt.strftime('%U'))-1)
    #print int(dt.isoweekday())
    now = datetime.datetime.now()
    day, hour = now.isoweekday(),now.strftime("%H")

    timenow = time.localtime()
    #print day,hour
    #print dt.strftime('%H')
    #print dt.strftime('%Z')
    #for (tmp, name) in zip(QUOTATION_DB_PREFIX, QUOTATION_DB_PERIOD):
    #    print tmp,name

def dict_test():
    recordPeriodDict = {}
    dicttmp = {}
    atomicItem = dict(zip(QUOTATION_STRUCTURE,[0,0,0,0,'']))
    for tag in list(QUOTATION_DB_PERIOD):
        dicttmp = {tag: atomicItem}
        recordPeriodDict.update(dicttmp)

    print recordPeriodDict

def idiot():
    print "idiot"

def thread_test():
    '''main routine'''
    #dtScrp = DataScrape()
    #tm = TimerMotor(dtScrp.queryInfo,dtScrp.idiot,dtScrp.idiot)
    #tm.startTimer()

    #print tm.getFastTMCBFuncResult()
    t1 = threading.Thread(target=func)
    t2 = threading.Thread(target=func)
    t1.start()
    t2.start()

    time.sleep(2)
    # 发送事件通知
    #print 'MainThread set event.'
    event.set()

def talib_func():
    func_collection = talib.get_functions()
    for i in func_collection:
        print i

    func_dict = talib.get_function_groups()
    # 迭代器
    for item in func_dict.iteritems():
        print item

def numpy_data():
    data_analyse = numpy.random.random(10)
    print type(data_analyse)

def talib_sma_test():
    data_analyse = {
        'open':numpy.random.random(100),
        'high':numpy.random.random(100),
        'low':numpy.random.random(100),
        'close':numpy.random.random(100),
        'volume':numpy.random.random(100)
    }
    #close = numpy.random.random(100)
    #output = talib.SMA(close)
    output = talib.abstract.SMA(data_analyse, timeperiod=20, price='open')
    print (output)


def get_property():
    """ 内部接口API：根据XML配置文件读取相关属性字段 """
    fileName = 'Properties.xml'

    if not os.path.exists(fileName):
        return

    try:
        tree = ET.parse(fileName)
        root = tree.getroot()
    except Exception,e:
        print e.message
        return

    print root.tag, "---", root.attrib
    for child in root:
        print child.tag,'---' , child.attrib,'---',type(child)
    print len(root)
    print root[0][0].text
    print root[1][0].text

    for item in root.findall("data"):
        print item.find('value').text

def query_info():
    """东方财富网"""
    unknow_timestamp = "17209736178267005318"
    time_tick_beijin = (int(time.time()))*1000
    print (time_tick_beijin)
    ret_timestamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    ret_price = ''

    eastmoney_url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._SG&sty=MPNSBAS&st=c&sr=-1&p=1&ps=5&cb=jQuery%s_%s&js=([(x)])&token=7bc05d0d4c3c22ef9fca8c2a912d779c"%(unknow_timestamp,str(time_tick_beijin))
    r = requests.get(eastmoney_url)
    print r.text
    info_content = r.text.split('(')[1].split(')')[0]
    print info_content
    #print (info_content.split('%"'))
    for item in (info_content.split('%"')):
        #print (item)
        if item.find('XAG') != -1:
            #print item.split(',')
            ret_price = item.split(',')[4]
            break
    return [ret_price,ret_timestamp]

if __name__ == '__main__':
    #csv_test(db_test())
    #file_test()
    #talib_sma_test()
    #query_info()
    #get_property()
    db_test()
    sys.exit()