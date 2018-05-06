#coding=utf-8

import sqlite3
import os
import threading
import platform
import QuotationKit
from resource import Configuration
from resource import Constant
from resource import Primitive
from resource import Trace
import numpy as np
import pandas as pd
from pandas import DataFrame

class QuotationDB():
    """ 行情数据库类 """
    def __init__(self,flagList,recordDict):
        self.updatePeriodFlag = flagList
        self.recordPeriodDict = recordDict
        self.quoteCache = {}
        #程序启动时补全历史数据，为后续指标和策略计算做好准备
        for period in Constant.QUOTATION_DB_PREFIX[1:]:
            #查询当周是否有需要接续的数据记录
            quotefilename = Configuration.get_period_working_folder(period)+period+'-quote.db'
            if not os.path.exists(quotefilename):#当周程序首次运行，不存在对应数据库文件--需要创建
                dataSupplementWithID = DataFrame(columns=['id',]+list(Constant.QUOTATION_STRUCTURE))
                self.create_period_db(period)
            else:
                dataWithId = Primitive.translate_db_to_df(quotefilename)
                if dataWithId is not None and len(dataWithId) != 0:#若存在接续的数据记录
                    Trace.output('info'," === %s Period to be continued from QuoteDB === "%period)
                    for itemRow in dataWithId.itertuples():
                        Trace.output('info','    '+(' ').join(map(lambda x:str(x), itemRow)))

                    dataSupplementWithID = self.process_quotes_supplement(period,dataWithId)
                else:
                    dataSupplementWithID = dataWithId
            #print dataSupplementWithID#调试点
            #生成quote缓存DataFrame结构数据实例
            self.quoteCache.update({period: dataSupplementWithID})

    def process_quotes_supplement(self,period,dataWithID):
        """ 内部接口API：补全quotes数据
            periodName:周期名称的字符串
            dataWithID: dataframe结构的数据
            返回值: dateframe结构数据(id, time, open, high, low, close)
        """
        indx = Constant.QUOTATION_DB_PREFIX.index(period)
        dataCnt = dataWithID.iloc[-1:]['id']
        if len(dataCnt) == 0:
            cnt = 0#对于无记录文件情形，dataCnt为空的Series。int(dataCnt)会报错。
        else:
            cnt = int(dataCnt)
        gap = cnt-Constant.CANDLESTICK_PERIOD_CNT[indx]
        if gap >= 0:
            # 取从第（dataCnt-X个）到最后一个（第dataCnt）的数据（共X个）
            dataSupplementWithID = dataWithID.ix[int(gap):]
        else:# 要补齐蜡烛图中K线数目
            dataSupplementWithID = QuotationKit.supplement_quotes\
                (Configuration.get_period_working_folder(period),dataWithID,int(abs(gap)))

        return dataSupplementWithID

    def query_quote(self,periodName):
        """ 外部接口API: 获取某周期的quote缓存
            返回值：DataFrame结构数据
        """
        return self.quoteCache[periodName]

    def create_period_db(self,tagPeriod):
        """ 内部接口API: 创建数据库文件：行情数据库 """
        # 生成各周期时间数据库文件。心跳定时器的数据库文件冗余（忽略）。
        filePath = Configuration.get_period_working_folder(tagPeriod)+tagPeriod+'-quote.db'
        isExist = os.path.exists(filePath)
        if isExist:
            return
        db = sqlite3.connect(filePath)
        dbCursor = db.cursor()
        try:
            dbCursor.execute(Primitive.QUOTATION_DB_CREATE)
        except (Exception),e:
            Trace.output('fatal',"create quotation db file Exception: "+e.message)
        db.commit()
        dbCursor.close()
        db.close()

    def insert_period_db_opera(self, dbFile, priceList):
        """ 内部接口API: 更新各周期行情数据库 """
        db = sqlite3.connect(dbFile)
        dbCursor = db.cursor()
        #First: file should be existed
        #Second: insert some information
        try:
            dbCursor.execute(Primitive.QUOTATION_DB_INSERT, priceList)
        except (Exception),e:
            Trace.output('fatal',"insert item to quotation db Exception: " + e.message)

        db.commit()
        dbCursor.close()
        db.close()

    def update_period_db(self, period, priceList):
        """ 内部接口API: 行情数据库更新。对各周期数据库进行更新。
            period:定时器线程字符串名称，亦即对应数据库文件名抬头
            priceList:价格信息列表
        """
        # 每日结算期间只需要更新一次相关数据库
        if self.updatePeriodFlag[Constant.QUOTATION_DB_PREFIX.index(period)] == True:
            return
        #组装对应数据库文件路径
        dbFile = Configuration.get_period_working_folder(period)+period+'-quote.db'
        Trace.output('info','Period:%s '%period+'time out at %s '%priceList[0]+'open:%s'%priceList[1]+\
                     ' high:%s'%priceList[2]+' low:%s'%priceList[3]+' close:%s'%priceList[4])
        if priceList.count(0) != 0: # 若存在零值，则不插入数据库中。
            return
        self.insert_period_db_opera(dbFile, priceList)

        # 设置数据库更新标志
        self.updatePeriodFlag[Constant.QUOTATION_DB_PREFIX.index(period)] = True
        # 记录最小周期行情定时器到期

    def update_quote(self,periodName):
        """ 外部接口API: 定时器回调函数--更新某周期的quote缓存和db数据库文件
            入参：periodName--周期名称字符串
        """
        #更新Quote缓存
        dfQuote = self.quoteCache[periodName]
        dataBefore = np.array(dfQuote.ix[:])

        #挑取对应周期字典项
        prcDict = self.recordPeriodDict[periodName]
        priceInfo=[prcDict['time'],float(prcDict['open']),float(prcDict['high']),float(prcDict['low']),float(prcDict['close'])]
        #新增条目附着到原DataFrame实例后
        appendItem = np.array([dfQuote.shape[0],]+priceInfo)
        quotes = np.vstack((dataBefore,appendItem)) #按照时间顺序收集合并数据

        # 抬头信息
        title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)
        self.quoteCache[periodName] = DataFrame(quotes,columns=title)

        #更新数据库文件
        self.update_period_db(periodName,priceInfo)

