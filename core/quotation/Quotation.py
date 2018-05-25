#coding=utf-8

import sqlite3
import os
import threading
import platform
import QuotationKit
from resource import Configuration
from resource import Constant
from resource import Trace
import numpy as np
import pandas as pd
from pandas import DataFrame
from copy import deepcopy

class Quotation():
    """ 行情数据类 """
    def __init__(self,quoteRecordIns):
        self.baseTmCnt = 0#基本(驱动)定时器计数
        self.quoteRecord = quoteRecordIns
        self.updatePeriodFlag = quoteRecordIns.get_period_flag()
        self.recordPeriodDict = quoteRecordIns.get_record_dict()
        self.quoteTypeList = quoteRecordIns.get_stock_list()
        self.quoteCache = {}

        # 对于股票类型的周期行情数据缓存结构
        if self.quoteTypeList is not None:
            # 构建DF结构
            clmns = ['period']+list(Constant.QUOTATION_STRUCTURE)
            stockDF = DataFrame(columns=clmns)
            # 填充各统计周期行
            for period in Constant.QUOTATION_DB_PREFIX:
                stockDF = stockDF.append(dict(zip(clmns,[period,' ',0.0,0.0,0.0,0.0])),ignore_index=True)
            # 汇总各股票代码的字典项
            for stockID in self.quoteTypeList:
                self.quoteCache.update({stockID:deepcopy(stockDF)})
            return

        #程序启动时补全历史数据，为后续指标和策略计算做好准备
        for period in Constant.QUOTATION_DB_PREFIX:
            #查询当周是否有需要接续的数据记录
            quotefilename = Configuration.get_period_working_folder(period)+period+'-quote.csv'
            if not os.path.exists(quotefilename):#当周程序首次运行时不存在对应文件
                #dataSupplementWithID = DataFrame(columns=['id',]+list(Constant.QUOTATION_STRUCTURE))
                dataSupplementWithID = None
            else:
                dataWithId = pd.read_csv(quotefilename)
                if dataWithId is not None and len(dataWithId) != 0:#若存在接续的数据记录
                    Trace.output('info'," === %s Period to be continued from QuoteCSV === "%period)
                    for itemRow in dataWithId.itertuples():
                        Trace.output('info','    '+(' ').join(map(lambda x:str(x), itemRow)))

                    dataSupplementWithID = self.process_quotes_supplement(period,dataWithId)
                else:
                    dataSupplementWithID = dataWithId
            #print dataSupplementWithID#调试点
            #生成quote缓存DataFrame结构数据实例
            self.quoteCache.update({period: dataSupplementWithID})

    def increase_timeout_count(self):
        """ 外部接口API：基准更新定时器的到期计数值。基准更新定时器的回调函数调用。 """
        self.baseTmCnt+=1

    def remainder_higher_order(self,HOPeriod):
        """ 内/外部接口API：高阶定时器相对于基准更新定时器的余数。
                    如果余数是0，那么该定时器就到期。如果余数最大，那么是首次更新。
            返回值：余数值
            HOPeriod: 高阶定时器的周期字符串
        """
        dividend = Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(HOPeriod)]
        divisor = dividend/Constant.UPDATE_BASE_PERIOD
        return self.baseTmCnt%divisor

    def process_quotes_supplement(self,period,dataWithID):
        """ 内部接口API：补全quotes数据
            periodName:周期名称的字符串
            dataWithID: dataframe结构的数据
            返回值: dateframe结构数据(id, time, open, high, low, close)
        """
        cnt = len(dataWithID)
        indx = Constant.QUOTATION_DB_PREFIX.index(period)
        gap = cnt-Constant.CANDLESTICK_PERIOD_CNT[indx]
        if gap >= 0:
            # 取从第（dataCnt-X个）到最后一个（第dataCnt）的数据（共X个）
            dataSupplementWithID = dataWithID.ix[int(gap):]
        else:# 要补齐蜡烛图中K线数目
            dataSupplementWithID = QuotationKit.supplement_quotes\
                (Configuration.get_period_working_folder(period),dataWithID,int(abs(gap)))

        return dataSupplementWithID

    def query_quote(self,periodName):
        """ 外部接口API: 获取某周期的quote缓存。单一品种(期货/大宗商品)使用接口。
            返回值：DataFrame结构数据
        """
        return self.quoteCache[periodName]

    def update_stock_quote(self,stockID):
        """ 外部接口API: 周期行情数据缓存更新处理函数。基准更新定时器的回调函数。 """
        record = self.recordPeriodDict[stockID]

        # 更新基准定时器及高阶定时器的记录缓存
        for index,period in enumerate(Constant.QUOTATION_DB_PREFIX):
            stockDF = self.quoteCache[stockID]#在循环体内更新
            # 小于计数原子的周期不处理。
            if index < Constant.QUOTATION_DB_PERIOD.index(Constant.UPDATE_BASE_PERIOD):
                continue

            # 每次更新DF结构的前若干行len(Constant.QUOTATION_DB_PERIOD)之一
            remainder = self.remainder_higher_order(period)
            # 高阶定时器的一个周期完结，先存档条目
            if remainder == 0 and self.baseTmCnt != 0:
                # 将待存档的条目附着在本DataFrame结构后面。
                stockDF = stockDF.append(stockDF.ix[index],ignore_index=True)
                # 记录附加项(DF结构的最后一行)到日志文件中
                Trace.output('info',stockID+':Time out '+' '.join(list(stockDF.iloc[-1].astype(str))))

            # 再更新条目
            stockDF.ix[index,'time'] = record['time']
            stockDF.ix[index,'close'] = record['close']
            # 高阶定时器周期内的首次更新
            if remainder == 0:
                    stockDF.ix[index,'open'] = record['open']
                    stockDF.ix[index,'high'] = record['high']
                    stockDF.ix[index,'low'] = record['low']
            else:
                if stockDF.ix[index,'high'] < record['high']:
                    stockDF.ix[index,'high'] = record['high']
                if stockDF.ix[index,'low'] > record['low'] or stockDF.ix[index,'low'] == 0.0:
                    stockDF.ix[index,'low'] = record['low']
            self.quoteCache[stockID] = stockDF#数据回写
        #print self.quoteCache[stockID]#调试点
        self.quoteRecord.reset_stock_record(stockID)
        yield self.quoteCache[stockID]

    def update_period_flag(self, period, priceList):
        """ 内部接口API: 行情更新标志。
            period:定时器线程字符串名称
            priceList:价格信息列表
        """
        # 每日结算期间只需要更新一次
        if self.updatePeriodFlag[Constant.QUOTATION_DB_PREFIX.index(period)] == True:
            return
        Trace.output('info','Period:%s '%period+'time out at %s '%priceList[0]+'open:%s'%priceList[1]+\
                     ' high:%s'%priceList[2]+' low:%s'%priceList[3]+' close:%s'%priceList[4])
        if priceList.count(0) != 0: # 若存在零值，则不更新
            return
        # 更新标志
        self.updatePeriodFlag[Constant.QUOTATION_DB_PREFIX.index(period)] = True

    def update_quote(self,periodName):
        """ 外部接口API: 定时器回调函数--更新某周期的quote缓存
            入参：periodName--周期名称字符串
        """
        #挑取对应周期字典项
        prcDict = self.recordPeriodDict[periodName]
        priceInfo=[prcDict['time'].strftime("%Y-%m-%d %H:%M:%S"),prcDict['open'],\
                   prcDict['high'],prcDict['low'],prcDict['close']]

        #更新Quote缓存
        dfQuote = self.quoteCache[periodName]
        column = ['id',]+list(Constant.QUOTATION_STRUCTURE)
        if dfQuote is None:
            self.quoteCache[periodName] = DataFrame(dict(zip(column,[0,]+priceInfo)),index=[0],columns=column)
        else:#新增条目附着到原DataFrame实例后。新增条目的id是DF结构数据最后条目'id'加一，而非DF结构数据的长度
            id = int(dfQuote.iloc[-1]['id'])+1
            insertedDf = DataFrame(dict(zip(column,[id,]+priceInfo)),index=[id],columns=column)
            #按照时间顺序收集合并数据
            self.quoteCache[periodName] = self.quoteCache[periodName].append(insertedDf)

        #更新标志
        self.update_period_flag(periodName,priceInfo)

