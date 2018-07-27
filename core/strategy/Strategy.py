#coding=utf-8

import os
import copy
from copy import deepcopy
import pandas as pd
from pandas import DataFrame
from resource import Constant
from resource import DataSettleKit
from resource import Configuration

class Strategy():
    """
        策略算法模块
    """
    def __init__(self,targetList):
        """ 初始化 """
        self.targetList = targetList
        #蜡烛图组合模式DataFrame结构化
        dictPattern = {'Note':Constant.CANDLESTICK_PATTERN_NOTE, 'Pattern':Constant.CANDLESTICK_PATTERN}
        self.notePattern = DataFrame(dictPattern,index=range(len(Constant.CANDLESTICK_PATTERN)))

        #各周期策略生成后的记录DataFrame对象字典。该对象记录K线组合模式（可能有多条），然后再生成盈亏数据库记录条目，最后进行清理。
        self.dictPolRec = {}
        #该字典的键为标的名称字符串，值为DataFrame条目（见下）
        valueDf = DataFrame(columns=Constant.SER_DF_STRUCTURE)#建立空的DataFrame数据结构
        for target in self.targetList:
            file = Configuration.get_working_directory()+'%s-ser.csv'%target
            preWeekFile = Configuration.get_back_week_directory(file,1)+'%s-ser.csv'%target
            #补全历史数据
            if os.path.exists(file):
                self.dictPolRec.update({target:deepcopy(DataSettleKit.process_ser_supplement(target,file))})
            elif os.path.exists(preWeekFile):#周一开盘时接续上周条目
                self.dictPolRec.update({target:deepcopy(DataSettleKit.process_ser_supplement(target,preWeekFile))})
            else:#若本周及上周都无历史数据，则空白
                self.dictPolRec.update({target:deepcopy(valueDf)})

    def get_notePattern(self):
        return self.notePattern

    def get_strategy(self,target):
        """ 外部接口API: 获取某周期的策略记录
            target: 标的字符串
        """
        return self.dictPolRec[target]

    def set_strategy(self,target,dfInsert):
        """ 外部接口API: 获取某周期的策略记录
            target: 标的字符串
        """
        self.dictPolRec[target] = self.dictPolRec[target].append(dfInsert,ignore_index=True)
