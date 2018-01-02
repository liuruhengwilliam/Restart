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
        self.filePath = None

    def create_stratearnrate_db(self):
        """ 外部接口API: 创建数据库文件 """
        dt = datetime.datetime.now()
        year,week = dt.strftime('%Y'),dt.strftime('%U')
        #各周期创建所属的策略盈亏率数据库
        for tagPeriod in Constant.QUOTATION_DB_PREFIX[1:]:
            self.filePath = Configuration.get_period_working_folder(tagPeriod)+tagPeriod+'-ser.db'
            #生成数据库文件
            isExist = os.path.exists(self.filePath)
            db = sqlite3.connect(self.filePath)
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

    def update_peak_stratearnrate_db(self, value,time):
        """ 外部接口API:更新盈亏数据库中所有条目的盈亏峰值数据
            最小周期定时器到期时，遍历盈亏数据库中所有条目并对每个条目的峰值进行更新
        value:当前价格值
        time:当前时间
        """
        # 首先取出所有条目的极值
        db = sqlite3.connect(self.filePath)
        dbCursor = db.cursor()
        try:
            results = dbCursor.execute(Primitive.query_stratearnrate_db('id, direction, maxEarn, minEarn'))
            ret = results.fetchall()# 获取所有条目的这四个字段
            Trace.output('info','update peak earnrate db:\n'+ret)
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
            else:#‘空’方向 -- maxEarn值小于minEarn值
                if value < item[2]:
                    column = 'maxEarn'
                elif value > item[3]:#超越了极值就需要更新
                    column = 'minEarn'

            #如果当前值超越极值区间就更新相应的极值项
            try:
                if column != '':
                    dbCursor.execute(Primitive.update_stratearnrate_db(item[0],column,value))
                    Trace.output('info','  update item in peak stratearnrate db:\n'+'  '+item)
            except (Exception),e:
                Trace.output('fatal',"update peak vaule in stratearnrate db Exception: " + e.message)

        db.commit()
        dbCursor.close()
        db.close()

    def insert_item_stratearnrate_db(self, dirct,price,time,determineList):
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
            Trace.output('fatal',"insert into stratearnrate db Exception: " + e.message)
        db.commit()# 先提交
        # 获取该条目在数据库中对应的id值
        try:
            results = dbCursor.execute(Primitive.query_stratearnrate_db('id'))
            id = len(results.fetchall())
        except (Exception),e:
            Trace.output('fatal',"query stratearnrate db file Exception: "+e.message)

        dbCursor.close()
        db.close()

        return id

    def update_period_stratearnrate_db(self, value,period,id):
        """ 外部接口API:由链式定时器更新某周期数值
            链式定时器的回调函数。
            value：当前价格值
            period:周期名--字符串
            id:盈利数据库该条目id---非常重要
        """
        db = sqlite3.connect(self.filePath)
        dbCursor = db.cursor()
        try:
            column = period + 'Earn'
            dbCursor.execute(Primitive.update_stratearnrate_db(id,column,value))
        except (Exception),e:
            Trace.output('fatal',"update %sEarn in stratearnrate db Exception: "% period + e.message)
        db.commit()
        dbCursor.close()
        db.close()
