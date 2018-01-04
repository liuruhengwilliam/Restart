#coding=utf-8

import os
import sqlite3
import datetime
from resource import Configuration
from resource import Constant
from resource import Primitive
from resource import Trace

class StratEarnrateDB():
    """ 策略盈亏率数据库：
            功能描述：
                协作模块初始化数据库（搭建数据库结构）
                由strategy模块进行插入（条目的前若干字段，比如：多/空，判定周期，时间）操作。
                chain定时器（Start类中启动）进行更新（操作策略之后若干周期时间点的盈亏情况）。
            接口API：
                创建
                查询
                插入
                更新
    """
    def __init__(self,path):
        """
            path:数据库文件路径
        """
        #self.filePath = None

    def create_stratearnrate_db(self):
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

    def insert_item_stratearnrate_db(self, periodName, dfStrategy):
        """ 外部接口API:策略产生点时，插入该策略条目信息。
            可随同最小周期定时器调用。
            periodName: 周期名称字符串
            dfStrategy: DataFrame结构策略数据
            返回值: 数据库条目的游标 -- 指向第一个需要启动链式定时器的条目
        """
        indxMarked = 0
        filePath = Configuration.get_period_working_folder(periodName)+periodName+'-ser.db'
        db = sqlite3.connect(filePath)
        dbCursor = db.cursor()
        #获取该条目在数据库中对应的id值 -- 游标
        try:
            results = dbCursor.execute('select * from stratearnrate')
            indxMarked = len(results.fetchall())
        except (Exception),e:
            Trace.output('fatal',"query stratearnrate db file Exception: "+e.message)
        #DataFrame数据插入到SER数据库中
        #for itemRow in dfStrategy.itertuples(): #此法虽然效率较高，但是不便于后续维护。
        for indx in range(len(dfStrategy)):
            #dfStrategy.iloc[indx]可以获取整行数值
            dbItem = [str(dfStrategy.loc[indx,['time']].values),float(dfStrategy.loc[indx,['close']].values),\
                int(dfStrategy.loc[indx,['value']].values),periodName,str(dfStrategy.loc[indx,['pattern']].values)]
            try:
                dbCursor.execute(Primitive.STRATEARNRATE_DB_INSERT,dbItem)
            except (Exception),e:
                Trace.output('fatal',"insert into stratearnrate db Exception: " + e.message)

        db.commit()# 提交
        dbCursor.close()
        db.close()
        return indxMarked

    def update_period_stratearnrate_db(self, value,period,id):
        """ 外部接口API:由链式定时器更新某周期数值
            链式定时器的回调函数。
            value：当前价格值
            period:周期名--字符串
            id:盈利数据库该条目id---非常重要
        """
        filePath = Configuration.get_period_working_folder(tagPeriod)+tagPeriod+'-ser.db'
        db = sqlite3.connect(filePath)
        dbCursor = db.cursor()
        try:
            column = period + 'Earn'
            dbCursor.execute(Primitive.update_stratearnrate_db(id,column,value))
        except (Exception),e:
            Trace.output('fatal',"update %sEarn in stratearnrate db Exception: "% period + e.message)
        db.commit()
        dbCursor.close()
        db.close()
