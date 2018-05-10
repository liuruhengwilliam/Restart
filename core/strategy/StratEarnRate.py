#coding=utf-8

import os
import sqlite3
import datetime
import numpy as np
import pandas as pd
from pandas import DataFrame
from resource import Configuration
from resource import Constant
from resource import Primitive
from resource import Trace

# 策略盈亏率DataFrame和数据库操作：
#    功能描述：
#        由strategy模块进行插入（条目的前若干字段，比如：多/空，判定周期，时间）操作。
#        chain定时器（Start类中启动）进行更新（操作策略之后若干周期时间点的盈亏情况）。
#    接口API：创建/查询/插入/更新

def create_stratearnrate_db(tagPeriod):
    """ 外部接口API: 创建数据库文件 """
    dt = datetime.datetime.now()
    year,week = dt.strftime('%Y'),dt.strftime('%U')
    #各周期创建所属的策略盈亏率数据库
    filePath = Configuration.get_period_working_folder(tagPeriod)+tagPeriod+'-ser.db'
    #生成数据库文件
    isExist = os.path.exists(filePath)
    if isExist:
        return
    db = sqlite3.connect(filePath)
    dbCursor = db.cursor()
    try:
        dbCursor.execute(Primitive.STRATEARNRATE_DB_CREATE)
    except (Exception),e:
        Trace.output('fatal',"create stratearnrate db file Exception: "+e.message)
    db.commit()
    dbCursor.close()
    db.close()

def insert_stratearnrate_db(periodName,dfStrategy):
    """ 外部接口API:策略产生点时，插入该策略条目信息。
        可随同最小周期定时器调用。
        periodName: 周期名称字符串
        dfStrategy: DataFrame结构的策略数据
    """
    filePath = Configuration.get_period_working_folder(periodName)+periodName+'-ser.db'
    db = sqlite3.connect(filePath)
    dbCursor = db.cursor()
    #DataFrame数据插入到SER数据库中
    for itemRow in dfStrategy.itertuples(index=False):
        #dfStrategy.iloc[indx]可以获取整行数值
        #只有新增条目才需要插入---新增条目的'M15maxEarn'栏必定为0（充要条件）
        if 0 != itemRow[Constant.SER_DF_STRUCTURE.index('M15maxEarn')]:
            continue
        Trace.output('info','  insert into SER-DB with item: '+(' ').join(map(lambda x:str(x), itemRow)))
        try:
            #刨开DataFrame中特有项
            dbCursor.execute(Primitive.STRATEARNRATE_DB_INSERT,itemRow[2:])
        except (Exception),e:
            Trace.output('fatal',"insert into stratearnrate db Exception: " + e.message)

    db.commit()# 提交
    dbCursor.close()
    db.close()
