#coding=utf-8

import os
import sys
import talib
import traceback
import time
import datetime
import threading
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
    def __init__(self,quoteRecordIns):
        """ 初始化 """
        self.targetList = quoteRecordIns.get_target_list()
        #蜡烛图组合模式DataFrame结构化
        tplCandlestickPattern = {'Note':Constant.CANDLESTICK_PATTERN_NOTE, 'Pattern':Constant.CANDLESTICK_PATTERN}
        self.dfCandlestickPattern = DataFrame(tplCandlestickPattern,index=range(len(Constant.CANDLESTICK_PATTERN)))

        #各周期策略生成后的记录DataFrame对象字典。该对象记录K线组合模式（可能有多条），然后再生成盈亏数据库记录条目，最后进行清理。
        self.dictPolRec = {}
        #该字典的键为标的名称字符串，值为DataFrame条目（见下）
        valueDf = DataFrame(columns=Constant.SER_DF_STRUCTURE)#建立空的DataFrame数据结构
        for target in self.targetList:
            filename = Configuration.get_working_directory()+'%s-ser.csv'%target
            if os.path.exists(filename):#非首次运行就存在数据库文件
                valueDf = pd.read_csv(filename)
                if valueDf is not None and len(valueDf) != 0:#若存在接续的数据记录
                    Trace.output('info',"=== To be continued from %s SerCSV ==="%target)
                    for itemRow in valueDf.itertuples(index=False):
                        Trace.output('info','    '+(' ').join(map(lambda x:str(x), itemRow)))

            self.dictPolRec.update({target:deepcopy(valueDf)})

    def get_strategy(self,target):
        """ 外部接口API: 获取某周期的策略记录
            target: 标的字符串
        """
        return self.dictPolRec[target]

    def check_candlestick_pattern(self,target,data):
        """ 内部接口API: 蜡烛图组合图形的识别
            target:标的字符串
            data: 来自行情数据库的dataframe结构数据(已补全)
        """
        tmName = data.period[data.index[0]]
        dfCollect = DataFrame(columns=Constant.SER_DF_STRUCTURE)#收集本周期内新增策略条目
        for indxs in self.dfCandlestickPattern.index:# 遍历所有已定义的蜡烛图组合模型
            note = self.dfCandlestickPattern.loc[indxs]['Note']
            pattern = self.dfCandlestickPattern.loc[indxs]['Pattern']
            if note == 'alone':#对于'alone'类型K线组合暂不处理
                continue
            result = None
            try:
                result = getattr(talib, pattern)(data['open'].values,data['high'].values,data['low'].values,data['close'].values)
                # result是numpy.ndarray数据结构
                if len(result) != 0 and result.any() == True:
                    dataCache = copy.copy(data)#浅复制即可。若是赋值会污染‘data’；若是深拷贝会影响运行效率。
                    #关于浅拷贝和深拷贝说明的一篇文章 https://www.cnblogs.com/zxlovenet/p/4575228.html
                    dataCache[pattern] = result #增加蜡烛图组合模式的名称列
                    dfLastLine = dataCache[dataCache[pattern]!=0][-1:] #按照时间排序的最后一行即是更新行。返回DataFrame结构。

                    #dfLastLine['time'].values是numpy.ndarray类型
                    dealTmValue = str(dfLastLine['time'].values).strip('[\']')
                    if dealTmValue.find('/')!=-1:
                        dealTmValue = dealTmValue.replace('/','-')
                    if len(dealTmValue.split(':')) == 2:
                        targetTime = time.strptime(dealTmValue,"%Y-%m-%d %H:%M")
                    else:
                        targetTime = time.strptime(dealTmValue,"%Y-%m-%d %H:%M:%S")

                    #按照时间进行筛选。只添加不超过一个周期时间的条目。
                    nowFloat=time.mktime(time.strptime(str(datetime.datetime.now()).split('.')[0],'%Y-%m-%d %H:%M:%S'))
                    pttnFloat=time.mktime(targetTime)

                    if float(nowFloat-pttnFloat)>float(Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(tmName)]):
                        Trace.output('info','  find outdated strategy:%s'%pattern+' Time:%s'%dealTmValue+' in Period %s'%tmName)
                        continue
                    #匹配K线组合模式成功后，添加到本周期DataFrame记录对象中。相关统计项暂记为空值。
                    matchItem = [dealTmValue,float(dfLastLine['close'].values),tmName,pattern,int(dfLastLine[pattern].values),\
                                 '1900-01-01 00:00']+[0.0,'1900-01-01 00:00',10000.0,'1900-01-01 00:00']*7+[0,15*60]
                    #最后两项的含义：设置第一个周期是'15min'--序号为0，周期计数为15*60。
                    dfCollect = dfCollect.append(pd.Series(matchItem,index=Constant.SER_DF_STRUCTURE),ignore_index=True)
            except (Exception),e:
                exc_type,exc_value,exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_tb)
                traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))

        if len(dfCollect) != 0:
            #汇总到对应总表并添加数据库条目
            Trace.output('info','  === Period %s insert Strategy DateFrame ===  '%tmName)
            for itemRow in dfCollect.itertuples(index=False):
                Trace.output('info','    '+(' ').join(map(lambda x:str(x), itemRow)))

            if len(self.dictPolRec[target]) == 0:
                self.dictPolRec[target] = dfCollect
            else:
                self.dictPolRec[target] = self.dictPolRec[target].append(dfCollect,ignore_index=True)

    def check_strategy(self,target,data):
        """ 外部接口API: 检测行情，依据策略生成相关指令
            target:标的字符串
            data: 来自行情数据库的dataframe结构数据(已补全)
        """
        periodName = data.period[data.index[0]]
        indx = Constant.QUOTATION_DB_PREFIX.index(periodName)
        # 微尺度周期不匹配蜡烛图模式（减少策略生成的频度）
        if Constant.SCALE_CANDLESTICK[indx] < Constant.DEFAULT_SCALE_CANDLESTICK_PATTERN:
            return

        # 首先匹配蜡烛图组合
        self.check_candlestick_pattern(target,data)
        # 其次结合移动平均线和布林线进行分析

    def update_strategy(self,target,currentInfo):
        """ 外部接口API: 更新某周期的策略盈亏率数据。更新高阶定时器周期的SER数据。
            target:标的字符串
            currentInfo:当前时间和价格信息
        """
        closeTimeStr, highPrice, lowPrice = currentInfo#当前时间和价格信息
        if closeTimeStr.find('/')!=-1:
            closeTimeStr = closeTimeStr.replace('/','-')
        if len(closeTimeStr.split(':')) == 2:
            closeTime = datetime.datetime.strptime(closeTimeStr,"%Y-%m-%d %H:%M")
        else:
            closeTime = datetime.datetime.strptime(closeTimeStr,"%Y-%m-%d %H:%M:%S")

        if highPrice == 0.0 or lowPrice == 0.0:#对于抓取的异常数据不做处理
            return
        targetDF = self.dictPolRec[target]
        for period in Constant.QUOTATION_DB_PREFIX[2:-2]:
            #检查本周期DataFrame结构实例中是否有条目需要插入到数据库文件中。
            dfStrategy = targetDF[targetDF['period']==period]
            #print dfStrategy#调试点

            #for indx,itemRow in zip(dfStrategy.index,dfStrategy.itertuples(index=False)):
            for rowNo,itemRow in zip(range(len(dfStrategy)),dfStrategy.itertuples(index=False)):
                deadTimeIndx = Constant.SER_DF_STRUCTURE.index('DeadTime')
                #if itemRow[deadTimeIndx] != '':#DeadTime已经记录，不再更新。
                #    continue
                if itemRow[-2] >= Constant.SER_MAX_PERIOD:#最小周期从0开始计数故不能取MAX值。
                    continue

                # time项的异常处理
                baseTime = itemRow[Constant.SER_DF_STRUCTURE.index('time')]
                if baseTime.find('/')!=-1:
                    baseTime = baseTime.replace('/','-')
                if len(baseTime.split(':')) == 2:
                    baseTimeDT = datetime.datetime.strptime(baseTime,"%Y-%m-%d %H:%M")
                else:
                    baseTimeDT = datetime.datetime.strptime(baseTime,"%Y-%m-%d %H:%M:%S")

                #不更新过期（相对于策略盈亏条目的生成时间）的收盘价格。入参closeTime是datetime类型
                if closeTime < baseTimeDT:
                    continue
                try:
                    patternStr = itemRow[Constant.SER_DF_STRUCTURE.index('patternName')]
                    basePriceIndx = Constant.SER_DF_STRUCTURE.index('price')
                    dircIndx = Constant.SER_DF_STRUCTURE.index('patternVal')
                    basePrice = itemRow[basePriceIndx]
                    dirc = itemRow[dircIndx]
                    #'M15maxEarn'为记录项基址,itemRow[-2]*4为偏移量--链式定时序号。每四个记录项为一组。
                    XmaxEarnIndx = int(Constant.SER_DF_STRUCTURE.index('M15maxEarn'))+int(itemRow[-2]*4)
                    XmaxEarnTMIndx = XmaxEarnIndx+1
                    XmaxLossIndx = XmaxEarnIndx+2
                    XmaxLossTMIndx = XmaxEarnIndx+3
                    #注：Pandas元组中开头有自带Index项，所以下标有别于DataFrame结构。
                    #比对并更新（若需要）极值
                    #itemRow为Pandas元组，开头自带Index项，所以下标要加一。也可以通过index=False去掉最开头的索引。
                    if itemRow[XmaxEarnIndx]==0 or itemRow[XmaxLossIndx]==10000:#初始条目
                        if dirc > 0:#‘多’方向
                            dfStrategy.iat[rowNo,XmaxEarnIndx] = highPrice
                            dfStrategy.iat[rowNo,XmaxLossIndx] = lowPrice
                        else:#‘空’方向
                            dfStrategy.iat[rowNo,XmaxEarnIndx] = lowPrice
                            dfStrategy.iat[rowNo,XmaxLossIndx] = highPrice
                        dfStrategy.iat[rowNo,XmaxEarnTMIndx] = \
                        dfStrategy.iat[rowNo,XmaxLossTMIndx] = closeTimeStr
                    else:
                        if dirc > 0:#‘多’方向
                            if highPrice > itemRow[XmaxEarnIndx]:#大于最大盈利值
                                dfStrategy.iat[rowNo,XmaxEarnIndx] = highPrice
                                dfStrategy.iat[rowNo,XmaxEarnTMIndx] = closeTimeStr
                            if lowPrice < itemRow[XmaxLossIndx]:#小于最大亏损值
                                dfStrategy.iat[rowNo,XmaxLossIndx] = lowPrice
                                dfStrategy.iat[rowNo,XmaxLossTMIndx] = closeTimeStr
                        else:#‘空’方向 -- maxEarn值小于maxLoss值
                            if lowPrice<itemRow[XmaxEarnIndx]:#大于最大盈利值
                                dfStrategy.iat[rowNo,XmaxEarnIndx] = lowPrice
                                dfStrategy.iat[rowNo,XmaxEarnTMIndx] = closeTimeStr
                            if highPrice>itemRow[XmaxLossIndx]:#小于最大亏损值
                                dfStrategy.iat[rowNo,XmaxLossIndx] = highPrice
                                dfStrategy.iat[rowNo,XmaxLossTMIndx] = closeTimeStr

                    #判断是否止损，止损刻度时间的精度是5min。
                    if StrategyMisc.set_dead_price(basePrice,dirc,highPrice,lowPrice)==True:
                        Trace.output('warn','  == In Period %s, item DIED which bsTm %s bsPr %f dirc %d Pattern %s'\
                                     %(period,baseTime,basePrice,dirc,patternStr))
                        dfStrategy.iat[rowNo,deadTimeIndx] = closeTimeStr

                    #链式定时计数小于等于0说明有相关周期策略盈亏率统计周期要增加
                    if itemRow[-1] <= Constant.CHAIN_PERIOD[0]:
                        dfStrategy.iat[rowNo,-2] += 1 #设置链式定时的下个周期序号
                        #设置计数初值。需要减去前一个周期数值。
                        baseAddr = Constant.QUOTATION_DB_PERIOD.index(15*60)#周期计数值的基址
                        if itemRow[-2] < Constant.SER_MAX_PERIOD:# fix bug :'tuple index out of range'. Noted 20180301
                            dfStrategy.iat[rowNo,-1] = Constant.QUOTATION_DB_PERIOD[baseAddr+int(itemRow[-2])]
                    else:#链式计数还未到期
                        dfStrategy.iat[rowNo,-1] -= Constant.CHAIN_PERIOD[0]
                except (Exception),e:
                    exc_type,exc_value,exc_tb = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_tb)
                    traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))
