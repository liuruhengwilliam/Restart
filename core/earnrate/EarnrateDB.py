#coding=utf-8

import os
import sqlite3
import datetime
from resource import Configuration
from resource import Primitive
from resource import Trace

class EarnrateDB():
    """
        胜率数据库：
            功能描述：
                协作模块初始化数据库（搭建数据库结构）
                由strategy模块进行插入（条目的前若干字段，比如：多/空，判定周期，时间）操作。
                chain定时器（Start类中启动）进行更新（操作策略之后若干周期时间点的盈利情况）。
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
        self.id = 0 # 数据库条目id值--初值为0
        self.filePath = path

    def create_earnrate_db(self):
        """ 外部接口API: 创建数据库文件 """
        dt = datetime.datetime.now()
        year,week = dt.strftime('%Y'),dt.strftime('%U')
        fileName = year+'-'+week+'earnrate.db'
        self.filePath += '/'+fileName
        # 生成数据库文件
        isExist = os.path.exists(self.filePath)
        db = sqlite3.connect(self.filePath)
        dbCursor = db.cursor()
        #First: create db if empty
        if not isExist:
            try:
                dbCursor.execute(Primitive.EARNRATE_DB_CREATE)
            except (Exception),e:
                Trace.output('fatal',"create earnrate db file Exception: "+e.message)
        db.commit()
        dbCursor.close()
        db.close()

    def update_peak_earnrate_db(self, value,time,id):
        """ 外部接口API:更新盈利数据库中某条目的盈利峰值数据
            最小周期定时器到期时，遍历盈利数据库中所有条目并对每个条目的峰值进行更新
        value:当前价格值
        time:当前时间
        id:盈利数据库该条目id
        """
        # 首先取出该id条目的极值
        db = sqlite3.connect(self.filePath)
        dbCursor = db.cursor()
        try:
            results = dbCursor.execute(Primitive.query_earnrate_db('id, direction, maxEarn, minEarn'))
            ret = results.fetchall()# 获取所有条目的这四个字段
        except (Exception),e:
            Trace.output('fatal',"query earnrate db Exception: " + e.message)

        # 用当前值和每个条目的极值进行比较
        for item in ret:
            column = ''
            if item[1] == 'buy':#‘多’方向
                if value > item[2]:
                    column = 'maxEarn'
                elif value < item[3]:#超越了极值就需要更新
                    column = 'minEarn'
            else:#‘空’方向 -- maxEarn值小于minEarn
                if value < item[2]:
                    column = 'maxEarn'
                elif value > item[3]:#超越了极值就需要更新
                    column = 'minEarn'

            #如果当前值超越极值区间就更新相应的极值项
            try:
                if column != '':
                    dbCursor.execute(Primitive.update_earnrate_db(item[0],column,value))
            except (Exception),e:
                Trace.output('fatal',"update peak vaule in earnrate db Exception: " + e.message)

        db.commit()
        dbCursor.close()
        db.close()

    def insert_item_earnrate_db(self, dirct,price,time,determineList):
        """ 外部接口API:策略产生点时，插入该策略条目信息。
            可随同最小周期定时器调用。
            dirct: 策略方向
            price: 当前价格
            time: 当前时间
            determineList: 各周期策略的列表集合
            返回值: 数据库条目id -- 非常重要
        """
        db = sqlite3.connect(self.filePath)
        dbCursor = db.cursor()
        try:
            dbCursor.execute(Primitive.EARNRATE_DB_INSERT, [dirct,price,time,determineList])
        except (Exception),e:
            Trace.output('fatal',"insert into earnrate db Exception: " + e.message)
        db.commit()
        dbCursor.close()
        db.close()
        self.id += 1
        return self.id

    #更新周期时间点盈利值
    def update_period_earnrate_db(self, value,period,id):
        """ 外部接口API:更新链式定时器某周期数值
            链式定时器的回调函数。
            value：当前价格值
            period:周期名--字符串
            id:盈利数据库该条目id---非常重要
        """
        db = sqlite3.connect(self.filePath)
        dbCursor = db.cursor()
        try:
            column = period + 'Earn'
            dbCursor.execute(Primitive.update_earnrate_db(id,column,value))
        except (Exception),e:
            Trace.output('fatal',"update %sEarn in earnrate db Exception: "% period + e.message)
        db.commit()
        dbCursor.close()
        db.close()
