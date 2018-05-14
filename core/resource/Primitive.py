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

# id降序排列的查询原语 2017-11-13
QUOTATION_DB_QUERY_DESC = 'select * from quotation order by id desc'

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

def translate_db_to_df(dbFile):
    """ 外部接口API: 将db文件中的条目转换成dateframe格式
        dbFile: db文件名（含文件路径）
    """
    ret = None
    # db文件操作
    db = sqlite3.connect(dbFile)
    dbCursor = db.cursor()
    try:
        results = dbCursor.execute(QUOTATION_DB_QUERY_ASC)
        ret = results.fetchall()
    except (Exception),e:
        Trace.output("fatal", "Translate Exception: " + e.message)
    finally:
        dbCursor.close()
        db.close()
        if ret == None: return None

    # 写入抬头信息
    title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)
    if len(ret) == 0:
        dataframe = DataFrame(columns=title)
    else:
        dataframe = DataFrame(ret,columns=title)
    return dataframe
