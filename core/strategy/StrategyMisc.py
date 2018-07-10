#coding=utf-8

from resource import Constant
from resource import Configuration

def process_quotes_candlestick_pattern(data):
    """ 外部接口API:蜡烛图组合模式或图形的预处理函数
        data: dataframe结构的数据
        返回值：dateframe结构数据
    """
    periodName = data.period[data.index[0]]#直接获取'period'列的首项。由data.index[0]获取序号。
    indx = Constant.QUOTATION_DB_PREFIX.index(periodName)
    gap = len(data) - Constant.CANDLESTICK_PATTERN_MATCH_CNT[indx]

    if gap > 0:#截取指定数目记录。从第（dataCnt - Constant.CANDLESTICK_PATTERN_CNT[index]）行到最后一行
        data = data[int(abs(gap)):]

    return data

def set_dead_price(basePrice,dirc,highPrice,lowPrice):
    """外部接口API:检测价格是否超过止损线
       如果超过，返回True；否则返回False。
    """
    if dirc > 0:#“多”方向
        if float(lowPrice) > float(basePrice):
            return False
        deltaPrice = float(basePrice) - float(lowPrice)
    else:#“空”方向
        if float(basePrice) > float(highPrice):
            return False
        deltaPrice = float(highPrice) - float(basePrice)

    if deltaPrice/float(basePrice) >= Constant.STOP_LOSS_RATE:
        return True
    else:
        return False
