#coding=utf-8

import sys
import talib
import traceback
import time
import datetime
import numpy as np
import pandas as pd
import copy
from copy import deepcopy
from pandas import DataFrame
import StrategyMisc
from resource import Constant
from resource import Configuration
from resource import Trace

class Strategy():
    """
        策略算法模块
    """
    def __init__(self):
        """ 初始化 """
        #蜡烛图组合模式DataFrame结构化
        tplCandlestickPattern = {'Note':Constant.CANDLESTICK_PATTERN_NOTE, 'Pattern':Constant.CANDLESTICK_PATTERN}
        self.dfCandlestickPattern = DataFrame(tplCandlestickPattern,index=range(len(Constant.CANDLESTICK_PATTERN)))

        #各周期策略生成后的记录DataFrame对象字典。该对象记录K线组合模式（可能有多条），然后再生成盈亏数据库记录条目，最后进行清理。
        self.dfStrategyRecDict = {}
        #该字典的键为周期名称字符串，值为DataFrame条目（见下）。
        title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)+['pattern','value']
        valueDf = DataFrame(columns=title)#建立空的DataFrame数据结构

        for keyTag in Constant.QUOTATION_DB_PREFIX:
            self.dfStrategyRecDict.update({keyTag: deepcopy(valueDf)})

    def check_candlestick_pattern(self,periodName,dataWithId):
        """ 外部接口API: 蜡烛图组合图形的识别
            periodName: 周期名称的字符串
            返回值：DataFrame结构数据
        """
        dataDealed = StrategyMisc.process_quotes_candlestick_pattern(periodName,dataWithId)

        for indxs in self.dfCandlestickPattern.index:# 遍历所有已定义的蜡烛图组合模型
            note = self.dfCandlestickPattern.loc[indxs]['Note']
            pattern = self.dfCandlestickPattern.loc[indxs]['Pattern']
            if note == 'alone':#对于'alone'类型K线组合暂不处理
                continue
            result = None
            try:
                result = getattr(talib, pattern)(np.float64(dataDealed['open'].values),\
                    np.float64(dataDealed['high'].values),np.float64(dataDealed['low'].values),\
                    np.float64(dataDealed['close'].values))
                # result是numpy.ndarray数据结构
                if len(result) != 0 and result.any() == True:
                    dataCache = copy.copy(dataDealed)#浅复制即可。若是赋值会污染‘dataDealed’；若是深拷贝会影响运行效率。
                    #关于浅拷贝和深拷贝说明的一篇文章 https://www.cnblogs.com/zxlovenet/p/4575228.html
                    dataCache[pattern] = result #增加蜡烛图组合模式的名称列
                    dfLastLine = dataCache[dataCache[pattern]!=0][-1:] #按照时间排序的最后一行即是更新行。返回DataFrame结构。

                    #按照时间进行筛选。只添加不超过一个周期时间的条目。
                    nowTimeFloat = time.mktime(time.strptime(str(datetime.datetime.now()).split('.')[0],'%Y-%m-%d %H:%M:%S'))
                    #对unicode字符特殊处理
                    patternTimeFloat = time.mktime(time.strptime(str(dfLastLine['time'].values).split('\'')[1],'%Y-%m-%d %H:%M:%S'))
                    if float(nowTimeFloat-patternTimeFloat)>float(Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(periodName)]):
                        continue

                    title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)+['pattern','value']
                    #匹配K线组合模式成功后，添加到本周期DataFrame记录对象中。
                    matchItem = [int(dfLastLine['id'].values),dfLastLine['time'].values,float(dfLastLine['open'].values),float(dfLastLine['high'].values),\
                               float(dfLastLine['low'].values),float(dfLastLine['close'].values),pattern,int(dfLastLine[pattern].values)]
                    self.dfStrategyRecDict[periodName] = self.dfStrategyRecDict[periodName].append(pd.Series(matchItem,index=title),ignore_index=True)

                    Trace.output('info',(' ').join(map(lambda x:str(x), matchItem)))
            except (Exception),e:
                exc_type,exc_value,exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_tb)
                traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))

        return self.dfStrategyRecDict[periodName]

    def check_strategy(self,periodName,dataWithId):
        """ 外部接口API: 检测行情，依据策略生成相关指令
            periodName:周期名称字符串
            dataWithID: 来自行情数据库的dataframe结构数据
        """
        indx = Constant.QUOTATION_DB_PREFIX.index(periodName)
        # 微尺度周期不匹配蜡烛图模式（减少策略生成的频度）
        if Constant.SCALE_CANDLESTICK[indx] < Constant.DEFAULT_SCALE_CANDLESTICK_PATTERN:
            return
        # 首先匹配蜡烛图组合
        self.check_candlestick_pattern(periodName,dataWithId)
        # 其次结合移动平均线和布林线进行分析