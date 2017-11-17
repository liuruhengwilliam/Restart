#coding=utf-8

import csv
import sqlite3
import platform
import numpy as np
import pandas as pd
from pandas import Series,DataFrame
from resource import Configuration
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
    title = ['id'] + map(lambda x:x , Configuration.QUOTATION_STRUCTURE)
    csvWriter.writerow(title)

    # db文件操作
    db = sqlite3.connect(dbFile)
    dbCursor = db.cursor()
    try:
        results = dbCursor.execute(Primitive.QUOTATION_DB_QUERY_DESC)# 倒序方式查询
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
    title = ['id'] + map(lambda x:x , Configuration.QUOTATION_STRUCTURE)
    csvWriter.writerow(title)

    for item in listToDeal:
        csvWriter.writerow(item)
    csvFile.close()

def translate_db_to_df(dbFile, lineCnt):
    """ 外部接口API: 将db文件中的条目转换成dateframe格式
        dbFile: db文件名（含文件路径）
        lineCnt: 截取db条目数目。注：‘-1’表示全部转换。
    """
    ret = None
    # db文件操作
    db = sqlite3.connect(dbFile)
    dbCursor = db.cursor()
    try:
        results = dbCursor.execute(Primitive.QUOTATION_DB_QUERY_DESC)# 倒序方式查询
        if lineCnt == -1: # 获取所有条目
            ret = results.fetchall()
        else:# 获取指定数量的最近条目
            ret = results.fetchmany(lineCnt)
    except (Exception),e:
        Trace.output("fatal", " translate quotation Exception: " + e.message)
    finally:
        dbCursor.close()
        db.close()
        if ret == None: return None

    # 抬头信息
    title = ['id'] + map(lambda x:x , Configuration.QUOTATION_STRUCTURE)

    dataframe = DataFrame(ret,columns=title)
    print dataframe
