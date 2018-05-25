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
    def __init__(self):
        """ 初始化 """
        #蜡烛图组合模式DataFrame结构化
        tplCandlestickPattern = {'Note':Constant.CANDLESTICK_PATTERN_NOTE, 'Pattern':Constant.CANDLESTICK_PATTERN}
        self.dfCandlestickPattern = DataFrame(tplCandlestickPattern,index=range(len(Constant.CANDLESTICK_PATTERN)))

        #共享资源--数据库文件互斥锁
        self.dictMutexLock={}
        #检测5min~12hour的周期
        for keyTag in Constant.QUOTATION_DB_PREFIX[Constant.QUOTATION_DB_PERIOD.index(Constant.UPDATE_BASE_PERIOD):]:
            mutex = threading.Lock()
            self.dictMutexLock.update({keyTag: mutex})

        #各周期策略生成后的记录DataFrame对象字典。该对象记录K线组合模式（可能有多条），然后再生成盈亏数据库记录条目，最后进行清理。
        self.dictPolRec = {}
        #该字典的键为周期名称字符串，值为DataFrame条目（见下）。
        valueDf = DataFrame(columns=Constant.SER_DF_STRUCTURE)#建立空的DataFrame数据结构
        for keyTag in Constant.QUOTATION_DB_PREFIX[Constant.QUOTATION_DB_PERIOD.index(Constant.UPDATE_BASE_PERIOD):]:
            filename = Configuration.get_period_working_folder(keyTag)+keyTag+'-ser.csv'
            if os.path.exists(filename):#非首次运行就存在数据库文件
                valueDf = pd.read_csv(filename)
                if valueDf is not None and len(valueDf) != 0:#若存在接续的数据记录
                    Trace.output('info'," === %s Period to be continued from SerCSV === "%keyTag)
                    for itemRow in valueDf.itertuples(index=False):
                        Trace.output('info','    '+(' ').join(map(lambda x:str(x), itemRow)))

            self.dictPolRec.update({keyTag: deepcopy(valueDf)})

    def query_strategy_record(self,period):
        """ 外部接口API: 获取某周期的策略记录
            period: 周期字符串
        """
        return self.dictPolRec[period]

    def check_candlestick_pattern(self,tmName,dataDealed):
        """ 内部接口API: 蜡烛图组合图形的识别
            tmName: 定时器周期名称的字符串
            dataDealed: 来自行情数据库的dataframe结构数据(已补全)
        """
        dfCollect = DataFrame(columns=Constant.SER_DF_STRUCTURE)#收集本周期内新增策略条目
        for indxs in self.dfCandlestickPattern.index:# 遍历所有已定义的蜡烛图组合模型
            note = self.dfCandlestickPattern.loc[indxs]['Note']
            pattern = self.dfCandlestickPattern.loc[indxs]['Pattern']
            if note == 'alone':#对于'alone'类型K线组合暂不处理
                continue
            result = None
            try:
                result = getattr(talib, pattern)(dataDealed['open'].values,\
                    dataDealed['high'].values,dataDealed['low'].values,dataDealed['close'].values)
                # result是numpy.ndarray数据结构
                if len(result) != 0 and result.any() == True:
                    dataCache = copy.copy(dataDealed)#浅复制即可。若是赋值会污染‘dataDealed’；若是深拷贝会影响运行效率。
                    #关于浅拷贝和深拷贝说明的一篇文章 https://www.cnblogs.com/zxlovenet/p/4575228.html
                    dataCache[pattern] = result #增加蜡烛图组合模式的名称列
                    dfLastLine = dataCache[dataCache[pattern]!=0][-1:] #按照时间排序的最后一行即是更新行。返回DataFrame结构。

                    #dfLastLine['time'].values是numpy.ndarray类型
                    dealTmValue = str(dfLastLine['time'].values)
                    if dealTmValue.startswith('[u\''):
                        dealTmValue = dealTmValue.strip('[u\'\']')
                    elif dealTmValue.startswith('[datetime.datetime'):#拼装成同种格式
                        valueList = map(lambda x: x.strip(' '), dealTmValue.strip('[datetime.datetime()]').split(','))
                        dealTmValue = '-'.join(valueList[0:3])+' '+':'.join(valueList[3:])
                    elif dealTmValue.startswith('[\'') and dealTmValue.find('T')!=-1:
                        dealTmValue = dealTmValue.strip('[\'\']').replace('T',' ').strip('.0')#理解strip含义
                    elif dealTmValue.startswith('[\''):
                        dealTmValue = dealTmValue.strip('[\'\']')
                    else:
                        Trace.output('fatal',"  invalid target time %s"%str(dfLastLine['time'].values))
                        continue
                    targetTime = time.strptime(dealTmValue,'%Y-%m-%d %H:%M:%S')

                    #按照时间进行筛选。只添加不超过一个周期时间的条目。
                    nowFloat=time.mktime(time.strptime(str(datetime.datetime.now()).split('.')[0],'%Y-%m-%d %H:%M:%S'))
                    pttnFloat=time.mktime(targetTime)

                    if float(nowFloat-pttnFloat)>float(Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(tmName)]):
                        Trace.output('info','  find outdated strategy:%s'%pattern+' Time:%s'%dealTmValue+' in Period %s'%tmName)
                        continue
                    #匹配K线组合模式成功后，添加到本周期DataFrame记录对象中。相关统计项暂记为空值。
                    matchItem = [dealTmValue,float(dfLastLine['close'].values),tmName,pattern,int(dfLastLine[pattern].values),'1900-01-01 00:00']\
                                +[0.0,'1900-01-01 00:00',10000.0,'1900-01-01 00:00']*7+[0,15*60]
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

            self.dictMutexLock[tmName].acquire()
            if len(self.dictPolRec[tmName]) == 0:
                self.dictPolRec[tmName] = dfCollect
            else:
                self.dictPolRec[tmName] = self.dictPolRec[tmName].append(dfCollect,ignore_index=True)
            self.dictMutexLock[tmName].release()

    def check_strategy(self,periodName,dataWithId):
        """ 外部接口API: 检测行情，依据策略生成相关指令
            periodName:周期名称字符串
            dataWithID: 来自行情数据库的dataframe结构数据(已补全)
        """
        indx = Constant.QUOTATION_DB_PREFIX.index(periodName)
        # 微尺度周期不匹配蜡烛图模式（减少策略生成的频度）
        if Constant.SCALE_CANDLESTICK[indx] < Constant.DEFAULT_SCALE_CANDLESTICK_PATTERN:
            return

        # 首先匹配蜡烛图组合
        self.check_candlestick_pattern(periodName,dataWithId)
        # 其次结合移动平均线和布林线进行分析

    def update_strategy(self,currentInfo):
        """ 外部接口API: 更新某周期的策略盈亏率数据。
            更新15min/30min/1hour/2hour/4hour/6hour/12hour周期的SER数据
            currentInfo:当前时间和价格信息
        """
        closeTime, highPrice, lowPrice = currentInfo#当前时间和价格信息
        closeTimeStr = closeTime.strftime("%Y-%m-%d %H:%M")
        if highPrice == 0.0 or lowPrice == 0.0:#对于抓取的异常数据不做处理
            return
        for tmName in Constant.QUOTATION_DB_PREFIX[2:-2]:
            #检查本周期DataFrame结构实例中是否有条目需要插入到数据库文件中。此处只读访问，不进行资源互锁。
            self.dictMutexLock[tmName].acquire()
            dfStrategy = self.dictPolRec[tmName]

            if dfStrategy is None or len(dfStrategy) == 0:
                self.dictMutexLock[tmName].release()
                continue
            rowNo = -1#行号定义为-1，简化后续循环的逻辑处理
            for itemRow in dfStrategy.itertuples(index=False):
                rowNo+=1#行号自增
                deadTimeIndx = Constant.SER_DF_STRUCTURE.index('DeadTime')
                #if itemRow[deadTimeIndx] != '':#DeadTime已经记录，不再更新。
                #    continue
                if itemRow[-2] >= Constant.SER_MAX_PERIOD:#最小周期从0开始计数故不能取MAX值。
                    continue
                #不更新过期（相对于策略盈亏条目的生成时间）的收盘价格。入参closeTime是datetime类型
                if closeTime < datetime.datetime.strptime(itemRow[Constant.SER_DF_STRUCTURE.index('time')],"%Y-%m-%d %H:%M:%S"):
                    continue
                try:
                    patternStr = itemRow[Constant.SER_DF_STRUCTURE.index('patternName')]
                    baseTime = itemRow[Constant.SER_DF_STRUCTURE.index('time')]
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
                                     %(tmName,baseTime,basePrice,dirc,patternStr))
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

            self.dictMutexLock[tmName].release()
