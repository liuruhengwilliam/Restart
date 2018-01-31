#coding=utf-8

import os
import csv
import sqlite3
import datetime
from pandas import DataFrame
import Constant
import Trace

# 行情数据库操作原语
QUOTATION_DB_CREATE = 'create table quotation(\
    id integer primary key autoincrement not null default 1,\
    time float, open float, high float, low float, close float);'

# 插入操作
QUOTATION_DB_INSERT = 'insert into quotation (time,open,high,low,close)\
    values(?, ?, ?, ?, ?)'

# id升序排列的查询操作 2017-10-31
QUOTATION_DB_QUERY_ASC = 'select * from quotation'
SER_DB_QUERY_ASC = 'select * from stratearnrate'

# id降序排列的查询原语 2017-11-13
QUOTATION_DB_QUERY_DESC = 'select * from quotation order by id desc'
SER_DB_QUERY_DESC = 'select * from stratearnrate order by indx desc'

#=================================================================================
# 策略盈亏率数据库操作原语
# 建表
# 表结构说明：
#策略点时间，策略点价格，策略点方向，周期名称，技术指标名称（组合图形名称索引或其他）
#策略点给出后盈亏率时间统计:极值及时间15min/30min/1hour/2hour/4hour/6hour/12hour，损单时间（止损可配置，默认0.7%）
STRATEARNRATE_DB_CREATE = 'create table stratearnrate(\
    indx integer primary key autoincrement not null default 1,\
    time text, price float, tmName text, patternName text,patternVal int, DeadTime text,\
    M15maxEarn float, M15maxEarnTime text, M15maxLoss float, M15maxLossTime text,\
    M30maxEarn float, M30maxEarnTime text, M30maxLoss float, M30maxLossTime text,\
    H1maxEarn float, H1maxEarnTime text, H1maxLoss float, H1maxLossTime text,\
    H2maxEarn float, H2maxEarnTime text, H2maxLoss float, H2maxLossTime text,\
    H4maxEarn float, H4maxEarnTime text, H4maxLoss float, H4maxLossTime text,\
    H6maxEarn float, H6maxEarnTime text, H6maxLoss float, H6maxLossTime text,\
    H12maxEarn float, H12maxEarnTime text, H12maxLoss float, H12maxLossTime text,\
    tmChainIndx int, restCnt float);'

# 插入: 时间，价格，方向，周期名称，匹配模式名称
STRATEARNRATE_DB_INSERT=\
    'insert into stratearnrate(time,price,tmName,patternName,patternVal,DeadTime,\
    M15maxEarn, M15maxEarnTime, M15maxLoss, M15maxLossTime,\
    M30maxEarn, M30maxEarnTime, M30maxLoss, M30maxLossTime,\
    H1maxEarn, H1maxEarnTime, H1maxLoss, H1maxLossTime,\
    H2maxEarn, H2maxEarnTime, H2maxLoss, H2maxLossTime,\
    H4maxEarn, H4maxEarnTime, H4maxLoss, H4maxLossTime,\
    H6maxEarn, H6maxEarnTime, H6maxLoss, H6maxLossTime,\
    H12maxEarn, H12maxEarnTime, H12maxLoss, H12maxLossTime,\
    tmChainIndx,restCnt) \
    values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

def translate_db_into_csv(dbFile, lineCnt=-1):
    """ 外部接口API:将db文件转换成同名同路径的csv文件
        dbFile: db文件名（含文件路径）
        lineCnt: 截取db条目数目。注：‘-1’表示全部转换。
    """
    filename = '%s%s%s'%(dbFile.split('.')[0],str(datetime.date.today()),'.csv')
    if dbFile.split('.')[0][-3:] == 'ser':#获取db文件类型:行数数据or策略盈亏率数据
        fileType = 'Ser'
    else:
        fileType = 'Quote'

    if os.path.exists(filename):
        return
    csvFile = file(filename, 'wb')

    csvWriter = csv.writer(csvFile, dialect='excel')

    # 写入抬头信息
    if fileType == 'Ser':
        title = ['indx'] + map(lambda x:x , Constant.SER_DF_STRUCTURE[1:])
    else:
        title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)
    csvWriter.writerow(title)

    # db文件操作
    db = sqlite3.connect(dbFile)
    dbCursor = db.cursor()
    try:
        if fileType == 'Ser':#策略盈亏率数据
            results = dbCursor.execute(SER_DB_QUERY_ASC)
        else:
            results = dbCursor.execute(QUOTATION_DB_QUERY_ASC)# 正序方式查询

        if lineCnt == -1: # 获取所有条目
            ret = results.fetchall()
        else:# 获取指定数量的最近条目
            ret = results.fetchmany(lineCnt)
        # db查询条目插入到csv文件中。
        for item in ret:
            csvWriter.writerow(item)
    except (Exception),e:
        Trace.output("fatal", " translate %s Exception: "%fileType + e.message)
    csvFile.close()
    #db.commit()
    dbCursor.close()
    db.close()

def translate_db_to_df(dbFile):
    """ 外部接口API: 将db文件中的条目转换成dateframe格式
        dbFile: db文件名（含文件路径）
    """
    if dbFile.split('.')[0][-3:] == 'ser':#获取db文件类型:行数数据or策略盈亏率数据
        fileType = 'Ser'
    else:
        fileType = 'Quote'

    ret = None
    # db文件操作
    db = sqlite3.connect(dbFile)
    dbCursor = db.cursor()
    try:
        if fileType == 'Ser':#策略盈亏率数据
            results = dbCursor.execute(SER_DB_QUERY_ASC)
            ret = results.fetchall()
        else:
            results = dbCursor.execute(QUOTATION_DB_QUERY_ASC)
            ret = results.fetchall()
    except (Exception),e:
        Trace.output("fatal", " translate %s Exception: "%fileType + e.message)
    finally:
        dbCursor.close()
        db.close()
        if ret == None: return None

    # 写入抬头信息
    if fileType == 'Ser':
        title = ['indx'] + map(lambda x:x , Constant.SER_DF_STRUCTURE[1:])
    else:
        title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)
    if len(ret) == 0:
        dataframe = DataFrame(columns=title)
    else:
        dataframe = DataFrame(ret,columns=title)
    return dataframe
