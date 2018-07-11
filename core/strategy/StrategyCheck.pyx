#coding=utf-8

import sys
import time
import datetime
import traceback
import copy
import talib
import numpy as np
import pandas as pd
from pandas import DataFrame
from resource import Constant
from resource import Trace
from resource import Configuration

def mod_period_list(baseTmCnt):
    """ 外部接口API: 获取当前计数对各周期的去模列表。
        返回值： 取模之后的列表结构。
        baseTmCnt: 基础更新定时器的计数值
    """
    modList = [-1,-1]
    #from 15min to 1day对于股票型程序，由于每日自动退出，所以也不可能超过4hour。
    for period in Constant.QUOTATION_DB_PERIOD[2:-1]:
        modList.append(baseTmCnt%(period/Constant.UPDATE_BASE_PERIOD))
    modList.append(-1)
    return modList

def check_candlestick_pattern(data):
    """ 内部接口API: 蜡烛图组合图形的识别
        data: 来自行情数据库的dataframe结构数据(已补全)
    """
    #蜡烛图组合模式DataFrame结构化
    dictPattern = {'Note':Constant.CANDLESTICK_PATTERN_NOTE, 'Pattern':Constant.CANDLESTICK_PATTERN}
    notePattern = DataFrame(dictPattern,index=range(len(Constant.CANDLESTICK_PATTERN)))

    # 获取周期字符串
    tmName = data.period[data.index[0]]
    dfCollect = DataFrame(columns=Constant.SER_DF_STRUCTURE)#收集本周期内新增策略条目

    for indxs in notePattern.index:# 遍历所有已定义的蜡烛图组合模型
        note = notePattern.loc[indxs]['Note']
        pattern = notePattern.loc[indxs]['Pattern']
        if note == 'alone':#对于'alone'类型K线组合暂不处理
            continue
        result = None
        try:
            result = getattr(talib, pattern)(data['open'].values.astype(np.double),\
                                             data['high'].values.astype(np.double),\
                                             data['low'].values.astype(np.double),\
                                             data['close'].values.astype(np.double))
            # result是numpy.ndarray数据结构
            if len(result) != 0 and result.any() == True:
                dataCache = copy.copy(data)#浅复制即可。若是赋值会污染‘data’；若是深拷贝会影响运行效率。
                #关于浅拷贝和深拷贝说明的一篇文章 https://www.cnblogs.com/zxlovenet/p/4575228.html
                dataCache[pattern] = result #增加蜡烛图组合模式的名称列
                #按照时间排序的最后一行即是更新行。返回DataFrame结构。
                dfLastLine = dataCache[dataCache[pattern]!=0][-1:]

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
                         '1900-01-01 00:00:00']+[0.0,'1900-01-01 00:00:00',10000.0,'1900-01-01 00:00:00']*7+[0,15*60]
                #最后两项的含义：设置第一个周期是'15min'--序号为0，周期计数为15*60。
                dfCollect = dfCollect.append(pd.Series(matchItem,index=Constant.SER_DF_STRUCTURE),ignore_index=True)
        except (Exception),e:
            exc_type,exc_value,exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))

    if len(dfCollect) != 0:
        #汇总到对应总表并添加数据库条目
        Trace.output('info','  === Period %s insert Strategy DateFrame ===  '%tmName)
        for itemRow in dfCollect.itertuples(index=False):#调试点
            Trace.output('info','    '+(' ').join(map(lambda x:str(x), itemRow)))

    return dfCollect

def check_strategy(baseTmCnt,dfQuote):
    """ 外部接口API: 检测行情，依据策略生成相关指令
        target:标的字符串
        dfQuote: 来自行情数据库的dataframe结构数据(已补全)
    """
    for index,modVal in enumerate(mod_period_list(baseTmCnt)):
        if modVal != 0:
            continue

        # 异常数据对应的周期不更新/匹配
        if dfQuote.time[index] == ' ':
            Trace.output('warn','Skip period %d for strategy with zero record'%(index))
            continue

        # 按照时间次序排列，并删除开头的十一行（实时记录行）
        quoteFilterDF = dfQuote.iloc[len(Constant.QUOTATION_DB_PERIOD):]
        # 按周期挑选条目
        quotePeriodDF = quoteFilterDF[quoteFilterDF['period']==Constant.QUOTATION_DB_PERIOD[index]]
        # 若无记录，则无法进行模式匹配。
        dfLen = len(quotePeriodDF)
        if dfLen == 0:
            continue
        gap = dfLen - Constant.CANDLESTICK_PATTERN_MATCH_CNT[index]
        if gap > 0:
            dataDealed = quotePeriodDF[int(abs(gap)):]
        else:
            dataDealed = quotePeriodDF
        # 策略算法计算
        return check_candlestick_pattern(dataDealed)
