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
        self.baseTmCnt = 0#基本(驱动)定时器计数值
        self.quoteRecord = quoteRecordIns
        self.quoteList = quoteRecordIns.get_target_list()
        self.quoteCache = {}

        # 构建DF结构
        clmns = ['period']+list(Constant.QUOTATION_STRUCTURE)
        quoteDF = DataFrame(columns=clmns)
        # 填充各统计周期行
        for period in Constant.QUOTATION_DB_PREFIX:
            quoteDF = quoteDF.append(dict(zip(clmns,[period,' ',0.0,0.0,0.0,0.0])),ignore_index=True)

        # 汇总各标的字典项
        for target in self.quoteList:
            self.quoteCache.update({target:deepcopy(quoteDF)})

        #程序启动时补全历史数据，为后续指标和策略计算做好准备

    def increase_timeout_count(self):
        """ 外部接口API：基准更新定时器的到期计数值。基准更新定时器的回调函数调用。 """
        self.baseTmCnt+=1

    def remainder_higher_order_tm(self,HOPeriod):
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
            file = Configuration.get_working_directory()+'quote.csv'
            dataSupplementWithID = QuotationKit.supplement_quotes(file,dataWithID,abs(gap))

        return dataSupplementWithID

    def query_quote(self,target):
        """ 外部接口API: 获取某标的quote缓存。
            返回值：DataFrame结构数据
        """
        return self.quoteCache[target]

    def update_quote(self,target):
        """ 外部接口API: 周期行情数据缓存更新处理函数。基准更新定时器的回调函数。 """
        record = self.quoteRecord.get_record_dict(target)

        # 更新基准定时器及高阶定时器的记录缓存
        for index,period in enumerate(Constant.QUOTATION_DB_PREFIX):
            quoteDF = self.quoteCache[target]#在循环体内更新
            # 小于计数原子的周期不处理。
            if index < Constant.QUOTATION_DB_PERIOD.index(Constant.UPDATE_BASE_PERIOD):
                continue

            # 每次更新DF结构的前若干行len(Constant.QUOTATION_DB_PERIOD)之一
            remainder = self.remainder_higher_order_tm(period)
            # 高阶定时器的一个周期完结，先存档条目
            if remainder == 0 and self.baseTmCnt != 0:
                # 将待存档的条目附着在本DataFrame结构后面。
                quoteDF = quoteDF.append(quoteDF.ix[index],ignore_index=True)
                # 记录附加项(DF结构的最后一行)到日志文件中
                Trace.output('info',target+':Time out '+' '.join(list(quoteDF.iloc[-1].astype(str))))

            # 再更新条目
            quoteDF.ix[index,'time'] = record['time']
            quoteDF.ix[index,'close'] = record['close']
            # 高阶定时器周期内的首次更新
            if remainder == 0:
                    quoteDF.ix[index,'open'] = record['open']
                    quoteDF.ix[index,'high'] = record['high']
                    quoteDF.ix[index,'low'] = record['low']
            else:
                if quoteDF.ix[index,'high'] < record['high']:
                    quoteDF.ix[index,'high'] = record['high']
                if quoteDF.ix[index,'low'] > record['low'] or quoteDF.ix[index,'low'] == 0.0:
                    quoteDF.ix[index,'low'] = record['low']
            self.quoteCache[target] = quoteDF#数据回写
        #print self.quoteCache[target]#调试点
        self.quoteRecord.reset_target_record(target)
        return self.quoteCache[target]
