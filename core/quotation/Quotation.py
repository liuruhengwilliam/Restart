#coding=utf-8

import os
from resource import DataSettleKit
from resource import Configuration
from resource import Constant
from resource import Trace
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
        # 汇总各标的字典项
        for target in self.quoteList:
            quoteDF = DataFrame(columns=clmns)
            # 填充各统计周期行
            for period in Constant.QUOTATION_DB_PREFIX:
                quoteDF = quoteDF.append(dict(zip(clmns,[period,' ',0.0,0.0,0.0,0.0])),ignore_index=True)

            #程序启动时补全当周数据，为后续指标和策略计算做好准备
            file = Configuration.get_working_directory()+'%s-quote.csv'%target
            preWeekFile = Configuration.get_back_week_directory(file,1)+'%s-quote.csv'%target
            #补全历史数据
            if os.path.exists(file):
                quoteDF = quoteDF.append(DataSettleKit.process_quotes_supplement(target,file),ignore_index=True)
            elif os.path.exists(preWeekFile):#周一开盘时接续上周条目
                quoteDF = quoteDF.append(DataSettleKit.process_quotes_supplement(target,preWeekFile),ignore_index=True)

            self.quoteCache.update({target:deepcopy(quoteDF)})
            #print self.quoteCache[target]#调试点

    def increase_baseTM_cnt(self):
        """ 外部接口API：基准更新定时器的到期计数值。基准更新定时器的回调函数调用。 """
        self.baseTmCnt+=1

    def get_baseTM_cnt(self):
        """ 外部接口API：获取基准更新定时器的到期计数值。 """
        return self.baseTmCnt

    def get_quote(self,target):
        """ 外部接口API: 获取某标的quote缓存。
            返回值：DataFrame结构数据
        """
        return self.quoteCache[target]

    def set_quote(self,target,dfQuote):
        """ 外部接口API: 设置某标的quote缓存。数据回写接口。
            dfQuote：待回写的DataFrame结构数据
        """
        self.quoteCache[target] = dfQuote
