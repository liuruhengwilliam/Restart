#coding=utf-8

import numpy as np
from resource import Constant
from quotation import QuotationKit

def process_quotes_candlestick_pattern(periodName,dataWithID):
    """ 外部接口API:蜡烛图组合模式或图形的预处理函数
        periodName: 周期名称的字符串
        dataWithID: dataframe结构的数据
        返回值：dateframe结构数据
    """
    dataCnt = dataWithID.iloc[-1:]['id']
    indx = Constant.QUOTATION_DB_PREFIX.index(periodName)
    gap = Constant.CANDLESTICK_PATTERN_MATCH_CNT[indx] - int(dataCnt)

    if gap > 0:# 要补齐蜡烛图中K线数目
        dataWithID = QuotationKit.supplement_quotes(periodName,dataWithID,int(gap))
    else:# 截取指定数目记录。从第（dataCnt - Constant.CANDLESTICK_PATTERN_CNT[index]）行到最后一行
        dataWithID = dataWithID[int(abs(gap)):]

    #dataWithID.drop(dataWithID.columns[0:1], axis=1, inplace=True)#抛弃'id'栏
    return dataWithID

def set_dead_price(basePrice,dirc,highPrice,lowPrice,deadTime):
    """外部接口API:检测价格是否超过止损线
       如果超过，返回True；否则返回False。
    """
    if deadTime != '':#DeadTime已经记录，不再更新。
        return False

    if dirc > 0:#“多”方向
        deltaPrice = abs(basePrice - float(lowPrice))
    else:#“空”方向
        deltaPrice = abs(basePrice - float(highPrice))

    if deltaPrice/basePrice >= Constant.STOP_LOSS_RATE:
        return True
    else:
        return False
