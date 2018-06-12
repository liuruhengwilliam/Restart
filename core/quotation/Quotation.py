#coding=utf-8

import os
import sqlite3
import threading
import platform
from resource import DataSettleKit
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
        self.baseTmCnt = 1#基本(驱动)定时器计数值
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
            #程序启动时补全当周数据，为后续指标和策略计算做好准备
            file = Configuration.get_working_directory()+'%s-quote.csv'%target
            preWeekFile = Configuration.get_back_week_directory(file,1)+'%s-quote.csv'%target
            #补全历史数据
            if os.path.exists(file):
                self.quoteCache.update({target:deepcopy(DataSettleKit.process_quotes_supplement(target,file))})
            elif os.path.exists(preWeekFile):#周一开盘时接续上周条目
                self.quoteCache.update({target:deepcopy(DataSettleKit.process_quotes_supplement(target,preWeekFile))})
            else:#若本周及上周都无历史数据，则空白
                self.quoteCache.update({target:deepcopy(quoteDF)})

            #print self.quoteCache[target]#调试点

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

    def get_quote(self,target):
        """ 外部接口API: 获取某标的quote缓存。
            返回值：DataFrame结构数据
        """
        return self.quoteCache[target]

    def update_quote(self,target):
        """ 外部接口API: 周期行情数据缓存更新处理函数。基准更新定时器的回调函数。 """
        record = self.quoteRecord.get_record_dict(target)

        # 对于异常record数据，不更新quote.
        if record['time']==' ':
            Trace.output('warn','skip for update %s with zero record'%target)
            return self.quoteCache[target]
        # 驱动定时器列表序号
        motorPeriodIndx = Constant.QUOTATION_DB_PERIOD.index(Constant.UPDATE_BASE_PERIOD)
        # 更新基准定时器及高阶定时器的记录缓存
        for index,period in enumerate(Constant.QUOTATION_DB_PREFIX):
            quoteDF = self.quoteCache[target]#在循环体内更新
            # 小于计数原子的周期不处理。
            if index < motorPeriodIndx:
                continue
            # 不更新驱动定时周期的冗余项。高于驱动定时周期项需要更新且不会冗余（通过闭市时间来保证）
            if index == motorPeriodIndx and quoteDF.ix[index,'time'] == record['time']:
                Trace.output('warn',target+' get Cloned info at %s'%record['time'])
                continue

            # 更新条目的截止时间/close价格
            quoteDF.ix[index,'time'] = record['time']
            quoteDF.ix[index,'close'] = record['close']
            if self.baseTmCnt == 1:#更新基准定时器首次计数
                quoteDF.ix[index,'open'] = record['open']
                quoteDF.ix[index,'high'] = record['high']
                quoteDF.ix[index,'low'] = record['low']

            # 每次更新DF结构的前若干行len(Constant.QUOTATION_DB_PERIOD)之一
            remainder = self.remainder_higher_order_tm(period)
            # 高阶定时器的一个周期完结，先存档旧条目，后更新条目
            if remainder == 0:
                # 将待存档的条目附着在本DataFrame结构后面。
                quoteDF = quoteDF.append(quoteDF.ix[index],ignore_index=True)
                Trace.output('info',target+':Time out '+' '.join(list(quoteDF.iloc[-1].astype(str))))
                # 高阶定时器周期内的首次更新。
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
