#coding=utf-8

import os
import csv
import sqlite3
import datetime
import platform
import numpy as np
import pandas as pd
from pandas import DataFrame
from resource import Constant
from resource import Primitive
from resource import Trace

def translate_db_into_csv(dbFile, lineCnt):
    """ 外部接口API:将db文件转换成同名同路径的csv文件
        dbFile: db文件名（含文件路径）
        lineCnt: 截取db条目数目。注：‘-1’表示全部转换。
    """
    csvFile = file(dbFile.split('.')[0] + '.csv', 'wb')
    csvWriter = csv.writer(csvFile, dialect='excel')

    # 写入抬头信息
    title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)
    csvWriter.writerow(title)

    # db文件操作
    db = sqlite3.connect(dbFile)
    dbCursor = db.cursor()
    try:
        results = dbCursor.execute(Primitive.QUOTATION_DB_QUERY_ASC)# 正序方式查询
        if lineCnt == -1: # 获取所有条目
            ret = results.fetchall()
        else:# 获取指定数量的最近条目
            ret = results.fetchmany(lineCnt)
        # db查询条目插入到csv文件中。
        for item in ret:
            csvWriter.writerow(item)
    except (Exception),e:
        Trace.output("fatal", " translate quotation Exception: " + e.message)
    csvFile.close()
    #db.commit()
    dbCursor.close()
    db.close()

def translate_list_into_csv(listToDeal,csvFileName):
    """ 外部接口API:将列表转换成csv文件
        listToDeal: 列表
        csvfileName: csv文件名（含文件路径）
    """
    csvFile = file(csvFileName, 'wb')
    csvWriter = csv.writer(csvFile, dialect='excel')

    # 写入抬头信息
    title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)
    csvWriter.writerow(title)

    for item in listToDeal:
        csvWriter.writerow(item)
    csvFile.close()

def translate_db_to_df(dbFile, lineCnt=-1):
    """ 外部接口API: 将db文件中的条目转换成dateframe格式
        dbFile: db文件名（含文件路径）
        lineCnt: 截取db条目数目。注：‘-1’表示全部转换。
    """
    ret = None
    # db文件操作
    db = sqlite3.connect(dbFile)
    dbCursor = db.cursor()
    try:
        if lineCnt == -1: # 获取所有条目
            results = dbCursor.execute(Primitive.QUOTATION_DB_QUERY_ASC)
            ret = results.fetchall()
        else:# 获取指定数量的条目。需要倒序查询
            results = dbCursor.execute(Primitive.QUOTATION_DB_QUERY_DESC)
            ret = results.fetchmany(lineCnt)
    except (Exception),e:
        Trace.output("fatal", " translate quotation Exception: " + e.message)
    finally:
        dbCursor.close()
        db.close()
        if ret == None: return None

    # 抬头信息
    title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)

    dataframe = DataFrame(ret,columns=title)
    return dataframe

def supplement_quotes(path,dataWithID,supplementCnt):
    """ 外部接口API：补齐某个数目的行情序列。不考虑*.csv格式文件转换（可手动编辑）。
        path：当前周期数据库文件夹路径（包含文件名）
        dataWithID: 当前周期行情数据库文件的dataframe结构数据
        supplementCnt: 需要增补的数目
        返回值: 增补后的dateframe结构行情数据
    """
    quotes = np.array(dataWithID.ix[:])
    if (platform.system() == "Windows"):
        segment = path.split('\\')
    else:
        segment = path.split('/')

    if len(segment) < 2:# 数据库文件路径异常
        return dataWithID

    period = segment[-1] # 获取当前周期的数据库文件名 e.g: 5min.db
    weekGap = 1 # 从前一周开始搜索
    while supplementCnt > 0:
        someday = datetime.date.today() - datetime.timedelta(weeks=weekGap)
        year,week = someday.strftime('%Y'),someday.strftime('%U')# 获取前一周的年份和周数
        if (platform.system() == "Windows"):
            preDBfile = '\\'.join(segment[:-2]+['%s-%s'%(year,week),'%s'%period])
        else:
            preDBfile = '/'.join(segment[:-2]+['%s-%s'%(year,week),'%s'%period])

        if not os.path.exists(preDBfile): #若回溯文件完毕，则退出循环。
            break

        dataSupplementWithID = translate_db_to_df(preDBfile)
        dataSupplementCnt = dataSupplementWithID.iloc[-1:]['id']
        if int(dataSupplementCnt) >= supplementCnt: #已经能够补全，取后面的(supplementCnt)个数据
            dataSupplement = np.array(dataSupplementWithID.ix[int(dataSupplementCnt)-supplementCnt:])
        else: #还未补全数据继续循环
            dataSupplement = np.array(dataSupplementWithID.ix[:])

        weekGap+=1 #时间回溯
        supplementCnt-=int(dataSupplementCnt) #待补全的数据调整。若为负，则跳出循环。
        quotes = np.vstack((dataSupplement,quotes)) #按照时间顺序收集合并数据

    # 抬头信息
    title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)
    dataframe = DataFrame(quotes,columns=title)

    return dataframe
