#coding=utf-8

import sys
import talib
import traceback
import time
import datetime
import numpy as np
import pandas as pd
import copy
import threading
from copy import deepcopy
from pandas import DataFrame
import StrategyMisc
from resource import Constant
from resource import Configuration
from resource import Trace
from stratearnrate import StratEarnRate

class Strategy():
    """
        策略算法模块
    """
    def __init__(self):
        """ 初始化 """
        #蜡烛图组合模式DataFrame结构化
        tplCandlestickPattern = {'Note':Constant.CANDLESTICK_PATTERN_NOTE, 'Pattern':Constant.CANDLESTICK_PATTERN}
        self.dfCandlestickPattern = DataFrame(tplCandlestickPattern,index=range(len(Constant.CANDLESTICK_PATTERN)))

        #共享资源--数据库文件互斥锁
        self.dictMutexLock={}
        for keyTag in Constant.QUOTATION_DB_PREFIX:
            mutex = threading.Lock()
            self.dictMutexLock.update({keyTag: mutex})

        #各周期策略生成后的记录DataFrame对象字典。该对象记录K线组合模式（可能有多条），然后再生成盈亏数据库记录条目，最后进行清理。
        self.dictPolRec = {}
        #该字典的键为周期名称字符串，值为DataFrame条目（见下）。
        valueDf = DataFrame(columns=Constant.SER_DF_STRUCTURE)#建立空的DataFrame数据结构
        for keyTag in Constant.QUOTATION_DB_PREFIX:
            self.dictPolRec.update({keyTag: deepcopy(valueDf)})

    def check_candlestick_pattern(self,tmName,dataWithId):
        """ 外部接口API: 蜡烛图组合图形的识别
            periodName: 周期名称的字符串
            dataWithID: 来自行情数据库的dataframe结构数据
        """
        dataDealed = StrategyMisc.process_quotes_candlestick_pattern(tmName,dataWithId)
        dfCollect = DataFrame(columns=Constant.SER_DF_STRUCTURE)#收集本周期内新增策略条目
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
                    nowFloat=time.mktime(time.strptime(str(datetime.datetime.now()).split('.')[0],'%Y-%m-%d %H:%M:%S'))
                    #对unicode字符特殊处理
                    pttnFloat=time.mktime(time.strptime(str(dfLastLine['time'].values).split('\'')[1],'%Y-%m-%d %H:%M:%S'))
                    if float(nowFloat-pttnFloat)>float(Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(tmName)]):
                        Trace.output('info','  find outdated strategy:%s'%pattern + \
                                    ' Time:%s'%str(dfLastLine['time'].values).split('\'')[1]+' in Period %s'%tmName)
                        continue

                    #匹配K线组合模式成功后，添加到本周期DataFrame记录对象中。相关统计项暂记为空值。
                    matchItem = [int(dfLastLine['id'].values),str(dfLastLine['time'].values).split('\'')[1],\
                            float(dfLastLine['close'].values),tmName,pattern,int(dfLastLine[pattern].values),\
                            0,'',10000,'',0,0,0,0,0,0,0,0,0,0,0,Constant.CHAIN_PERIOD[0]]
                    dfCollect = dfCollect.append(pd.Series(matchItem,index=Constant.SER_DF_STRUCTURE),ignore_index=True)
            except (Exception),e:
                exc_type,exc_value,exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_tb)
                traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))

        if len(dfCollect) != 0:
            #汇总到对应总表并添加数据库条目
            Trace.output('info',' === %s Period insert Strategy DB === '%tmName)
            self.dictMutexLock[tmName].acquire()
            self.dictPolRec[tmName] = self.dictPolRec[tmName].append(dfCollect,ignore_index=True)
            StratEarnRate.insert_stratearnrate_db(tmName,dfCollect)
            self.dictMutexLock[tmName].release()

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

    def query_strategy(self,periodName):
        """ 外部接口API: 获取某周期的策略指示
            返回值：DataFrame结构数据
        """
        return self.dictPolRec[periodName]

    def update_strategy(self,currentInfo):
        """ 外部接口API: 更新某周期的策略盈亏率数据。
            更新15min/30min/1hour/2hour/4hour/6hour/12hour/1day/1week周期的SER数据
            currentInfo:当前时间和价格信息
        """
        closeTime, highPrice, lowPrice, closePrice = currentInfo#当前时间和价格
        for tmName in Constant.QUOTATION_DB_PREFIX[1:]:
            self.dictMutexLock[tmName].acquire()
            dfStrategy = self.dictPolRec[tmName]
            updatedIndxList = []
            for itemRow in dfStrategy.itertuples():
                #itemRow为Pandas元组，开头自带Index项
                tmChainIndx = Constant.SER_DF_STRUCTURE.index('M5Earn')+itemRow[-2]#链式定时序号
                if itemRow[-1] - Constant.CHAIN_PERIOD[0] <= 0:
                    #链式定时计数小于等于0说明有相关周期盈亏率需要更新
                    dfStrategy.ix[itemRow[0],[tmChainIndx]] = closePrice #设置该时间点的价格，后续转百分比
                    dfStrategy.ix[itemRow[0],[-2]] = itemRow[-2]+1 #设置链式定时的下个周期序号
                    dfStrategy.ix[itemRow[0],[-1]] = Constant.CHAIN_PERIOD[itemRow[-2]+1] #设置计数初值
                    updatedIndxList.append(itemRow[0])#记录DataFrame数据结构中的序号
                else:#链式计数还未到期
                    dfStrategy.ix[itemRow[0],[-1]] -= Constant.CHAIN_PERIOD[0]

                #比对并更新（若需要）极值
                dircIndx = Constant.SER_DF_STRUCTURE.index('patterVal')
                maxEarnIndx = Constant.SER_DF_STRUCTURE.index('maxEarn')
                maxEarnTMIndx = Constant.SER_DF_STRUCTURE.index('maxEarnTime')
                maxLossIndx = Constant.SER_DF_STRUCTURE.index('maxLoss')
                maxLossTMIndx = Constant.SER_DF_STRUCTURE.index('maxLossTime')
                #注：Pandas元组中开头有自带Index项，所以下标有别于DataFrame结构。
                if itemRow[maxEarnIndx+1]==0 or itemRow[maxLossIndx+1]==10000:#初始条目
                    if itemRow[dircIndx+1] > 0:#‘多’方向
                        dfStrategy.ix[itemRow[0],[maxEarnIndx]] = highPrice
                        dfStrategy.ix[itemRow[0],[maxLossIndx]] = lowPrice
                    else:#‘空’方向
                        dfStrategy.ix[itemRow[0],[maxEarnIndx]] = lowPrice
                        dfStrategy.ix[itemRow[0],[maxLossIndx]] = highPrice

                    dfStrategy.ix[itemRow[0],[maxEarnTMIndx]] = dfStrategy.ix[itemRow[0],[maxLossTMIndx]] = \
                        closeTime.strftime("%Y-%m-%d %H:%M")
                    if updatedIndxList.count(itemRow[0]) == 0:
                        updatedIndxList.append(itemRow[0])
                else:
                    if itemRow[dircIndx+1] > 0:#‘多’方向
                        if highPrice > itemRow[maxEarnIndx+1] or lowPrice < itemRow[maxLossIndx+1]:#避免重复添加
                            if updatedIndxList.count(itemRow[0]) == 0:
                                updatedIndxList.append(itemRow[0])#记录DataFrame数据结构中的序号
                        if highPrice>itemRow[maxEarnIndx+1]:#大于最大盈利值
                            dfStrategy.ix[itemRow[0],[maxEarnIndx]] = highPrice
                            dfStrategy.ix[itemRow[0],[maxEarnTMIndx]] = closeTime.strftime("%Y-%m-%d %H:%M")
                        if lowPrice<itemRow[maxLossIndx+1]:#小于最大亏损值
                            dfStrategy.ix[itemRow[0],[maxLossIndx]] = lowPrice
                            dfStrategy.ix[itemRow[0],[maxLossTMIndx]] = closeTime.strftime("%Y-%m-%d %H:%M")
                    else:#‘空’方向 -- maxEarn值小于maxLoss值
                        if lowPrice < itemRow[maxEarnIndx+1] or highPrice > itemRow[maxLossIndx+1]:
                            if updatedIndxList.count(itemRow[0]) == 0:
                                updatedIndxList.append(itemRow[0])
                        if lowPrice<itemRow[maxEarnIndx+1]:#大于最大盈利值
                            dfStrategy.ix[itemRow[0],[maxEarnIndx]] = lowPrice
                            dfStrategy.ix[itemRow[0],[maxEarnTMIndx]] = closeTime.strftime("%Y-%m-%d %H:%M")
                        if highPrice>itemRow[maxLossIndx+1]:#小于最大亏损值
                            dfStrategy.ix[itemRow[0],[maxLossIndx]] = highPrice
                            dfStrategy.ix[itemRow[0],[maxLossTMIndx]] = closeTime.strftime("%Y-%m-%d %H:%M")

            #需要更新的条目序号组合成列表，然后一次性操作数据库文件。这样效率较高。
            if len(updatedIndxList) != 0:
                Trace.output('info',' === %s Period update Strategy DB === '% tmName)
                StratEarnRate.update_stratearnrate_db(tmName, updatedIndxList, dfStrategy)

            self.dictMutexLock[tmName].release()
