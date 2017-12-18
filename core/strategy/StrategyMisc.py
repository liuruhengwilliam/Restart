#coding=utf-8

import numpy as np

from resource import Constant
from quotation import QuotationKit

def process_quotes_candlestick_pattern(index,file,dataWithID):
    """ 外部接口API:蜡烛图组合模式或图形的预处理函数
        index:周期序列的下标
        file：数据库文件全路径（包含文件名，蜡烛图文件保存路径同目录）
        dataWithID: dataframe结构的数据
        返回值：dateframe结构数据
    """
    dataCnt = dataWithID.iloc[-1:]['id']
    gap = Constant.CANDLESTICK_PATTERN_CNT[index] - int(dataCnt)

    if gap > 0:# 要补齐蜡烛图中K线数目
        dataWithID = QuotationKit.supplement_quotes(file,dataWithID,int(gap))
    else:# 截取指定数目记录。从第（dataCnt - Constant.CANDLESTICK_PATTERN_CNT[index]）行到最后一行
        dataWithID = dataWithID[int(abs(gap)):]

    #dataWithID.drop(dataWithID.columns[0:1], axis=1, inplace=True)#抛弃'id'栏
    return dataWithID