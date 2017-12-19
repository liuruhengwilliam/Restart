#coding=utf-8

import os
import platform
import datetime
import numpy as np
from matplotlib.dates import date2num
from resource import Constant
from quotation import QuotationKit
from resource import Trace

def process_quotes_drawing_candlestick(periodName,dataWithID):
    """ 外部接口API：处理quotes数据
        1.去掉id栏
        2.调用date2num函数转换datetime
        periodName:周期名称的字符串
        dataWithID: dataframe结构的数据
        返回值: numpy.array结构数据(time, open, high, low, close)
    """
    dataCnt = dataWithID.iloc[-1:]['id']
    indx = Constant.QUOTATION_DB_PREFIX.index(periodName)
    gap = int(dataCnt)-Constant.CANDLESTICK_PERIOD_CNT[indx]
    if gap >= 0:
        # 取从第（dataCnt-X个）到最后一个（第dataCnt）的数据（共X个）
        quotes = np.array(dataWithID.ix[int(gap):,['time','open','high','low','close']])
    else:# 要补齐蜡烛图中K线数目
        dataSupplementWithID = QuotationKit.supplement_quotes(periodName,dataWithID,int(abs(gap)))
        quotes = np.array(dataSupplementWithID.ix[:,['time','open','high','low','close']])

    for q in quotes:
        q[0] = datetime.datetime.strptime(q[0],"%Y-%m-%d %H:%M:%S")
        q[0] = date2num(q[0])

    return quotes