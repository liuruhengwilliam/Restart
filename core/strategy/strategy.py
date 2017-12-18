#coding=utf-8

import sys
import talib
import platform
import traceback
import numpy as np
import pandas as pd
from copy import deepcopy
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
        result = None
        dataCsv = deepcopy(dataDealed)
        try:
            result = getattr(talib, pattern)(np.float64(dataDealed['open'].values),\
                np.float64(dataDealed['high'].values),np.float64(dataDealed['low'].values),\
                np.float64(dataDealed['close'].values))
            # result是numpy.ndarray数据结构
            if len(result)!=0 and result.any()==True:
                dataCsv[pattern] = result # 增加蜡烛图组合模式的名称列
                if (platform.system() == "Windows"):
                    csvFile = '%s%s%s-%s.csv'%(file.split('.')[0],'\\',Constant.QUOTATION_DB_PREFIX[indx],pattern)
                else:
                    csvFile = '%s%s%s-%s.csv'%(file.split('.')[0],'/',Constant.QUOTATION_DB_PREFIX[indx],pattern)

                dataCsv[dataCsv[pattern]!=0].to_csv(csvFile,encoding='utf-8')

        except (Exception),e:
            exc_type,exc_value,exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))


def check_strategy(indx,file,dataWithId):
    """ 外部接口API: 检测行情，依据策略生成相关指令
        index:周期序列的下标
        file: 行情数据库文件(包含文件路径名)
        dataWithID: 来自行情数据库的dataframe结构数据
    """
    # 微尺度周期不匹配蜡烛图模式（减少策略生成的频度）
    if Constant.SCALE_CANDLESTICK[indx] < Constant.DEFAULT_SCALE_CANDLESTICK_PATTERN:
        return

    check_candlestick_pattern(indx,file,dataWithId)
