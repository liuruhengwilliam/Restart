#coding=utf-8

import sys
import talib
import traceback
import numpy as np
import pandas as pd
import StrategyMisc
from resource import Constant
from resource import Configuration


"""
    策略算法模块：提供策略算法接口API
"""

def check_candlestick_pattern(indx,file,dataWithId):
    """ 外部接口API: 蜡烛图组合图形的识别
    """
    dataDealed = StrategyMisc.process_quotes_candlestick_pattern(indx,file,dataWithId)

    for pattern in Constant.STRATEGY_CANDLESTICK:# 遍历蜡烛图组合模型
        try:
            result = getattr(talib, pattern)(dataDealed['open'].values,dataDealed['high'].values,\
                                             dataDealed['low'].values,dataDealed['close'].values)
            # result是numpy.ndarray数据结构
        except (Exception),e:
            exc_type,exc_value,exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))
        finally:
            if len(result)!=0 and result.any()==True:
                #print Constant.QUOTATION_DB_PREFIX[indx]+' period '+pattern,result.max(),result.min()
                dataDealed[pattern] = result

    dataDealed.to_csv(pattern+'.csv',encoding='utf-8')

def check_strategy(indx,file,dataWithId):
    """ 外部接口API: 检测行情，依据策略生成相关指令
        index:周期序列的下标
        file: 行情数据库文件(包含文件路径名)
        dataWithID: 来自行情数据库的dataframe结构数据
    """
    check_candlestick_pattern(indx,file,dataWithId)
