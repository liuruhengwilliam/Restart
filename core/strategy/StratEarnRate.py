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

def create_stratearnrate_db():
    """ 外部接口API: 创建数据库文件 """
    dt = datetime.datetime.now()
    year,week = dt.strftime('%Y'),dt.strftime('%U')
    #各周期创建所属的策略盈亏率数据库
    for tagPeriod in Constant.QUOTATION_DB_PREFIX[1:]:
        filePath = Configuration.get_period_working_folder(tagPeriod)+tagPeriod+'-ser.db'
        #生成数据库文件
        isExist = os.path.exists(filePath)
        db = sqlite3.connect(filePath)
        dbCursor = db.cursor()
        #First: create db if empty
        if not isExist:
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
    for itemRow in dfStrategy.itertuples():
        #dfStrategy.iloc[indx]可以获取整行数值
        Trace.output('info',(' ').join(map(lambda x:str(x), itemRow)))
        try:
            #刨开DataFrame中特有项
            dbCursor.execute(Primitive.STRATEARNRATE_DB_INSERT,itemRow[2:-2])
        except (Exception),e:
            Trace.output('fatal',"insert into stratearnrate db Exception: " + e.message)

    db.commit()# 提交
    dbCursor.close()
    db.close()

def update_stratearnrate_db(periodName,indxList,dfStrategy):
    """ 外部接口API:更新某周期的策略盈亏率数据库。由‘5min’周期定时函数进行调用。
        periodName:周期名--字符串
        indxList:待更新条目序号的列表
        dfStrategy: DataFrame结构的策略数据
    """
    filePath = Configuration.get_period_working_folder(periodName)+periodName+'-ser.db'
    db = sqlite3.connect(filePath)
    dbCursor = db.cursor()
    for indx in indxList:
        itemList = np.array(dfStrategy.iloc[indx]).tolist()
        Trace.output('info',(' ').join(map(lambda x:str(x), itemList)))
        try:
            dbCursor.execute('update stratearnrate set time=?,price=?,tmName=?,\
                patternName=?,patternVal=?,DeadTime=?,\
                M15maxEarn=?,M15maxEarnTime=?,M15maxLoss=?,M15maxLossTime=?,\
                M30maxEarn=?,M30maxEarnTime=?,M30maxLoss=?,M30maxLossTime=?,\
                H1maxEarn=?,H1maxEarnTime=?,H1maxLoss=?,H1maxLossTime=?,\
                H2maxEarn=?,H2maxEarnTime=?,H2maxLoss=?,H2maxLossTime=?,\
                H4maxEarn=?,H4maxEarnTime=?,H4maxLoss=?,H4maxLossTime=?,\
                H6maxEarn=?,H6maxEarnTime=?,H6maxLoss=?,H6maxLossTime=?,\
                H12maxEarn=?,H12maxEarnTime=?,H12maxLoss=?,H12maxLossTime=?,\
                where indx=%d'%(indx+1),itemList[1:-2])
        except (Exception),e:
            Trace.output('fatal',"update %sEarn in stratearnrate db Exception: "% periodName+e.message)
    db.commit()
    dbCursor.close()
    db.close()
