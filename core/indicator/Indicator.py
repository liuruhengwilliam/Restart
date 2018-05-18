#coding=utf-8

import MA
import CandleStick
import BollingerBands
import DataProcess
from resource import Constant
from copy import deepcopy
import datetime
from resource import Trace
class Indicator():
    """
        指标类。蜡烛图、移动平均线、布林带。
    """
    def __init__(self):
        ma = [0,]*len(Constant.MOVING_AVERAGE_LINE)
        bbands = [0,]*len(['upperBB','middleBB','lowerBB'])
        # 各周期的移动平均线指标记录字典
        self.indiMADict = {}
        self.indiBBandsDict = {}

        for tag in Constant.QUOTATION_DB_PREFIX:
            itemMA = {tag: deepcopy(ma)}
            itemBBands = {tag: deepcopy(bbands)}
            self.indiMADict.update(itemMA)
            self.indiBBandsDict.update(itemBBands)

    def process_indicator(self,periodName,dataWithId):
        """ 外部接口API: 计算指标
            periodName:周期名称的字符串（用于计算蜡烛图展示根数）
            dataWithId:行情数据库中dateframe结构的数据。
        """
        dataPicked = DataProcess.process_quotes_4indicator(periodName,dataWithId)

        #数据样本太小就不制图
        if len(dataPicked) < Constant.CANDLESTICK_PATTERN_MATCH_CNT[Constant.QUOTATION_DB_PREFIX.index(periodName)]:
            return
        #移动平均线
        for index,tag in zip(range(len(Constant.MOVING_AVERAGE_LINE)),Constant.MOVING_AVERAGE_LINE):
            self.indiMADict[periodName][index] = MA.compute_sma(dataPicked['close'].as_matrix(),tag)

        #布林线
        self.indiBBandsDict[periodName] = BollingerBands.compute_BBands(dataPicked['close'].as_matrix())

        self.show_indicator(periodName,dataPicked)

    def fetch_ma_indicator(self,periodName):
        """ 外部接口API:移动均线指标。通过周期字符串在移动平均线字典中查找。
            periodName: 周期名称的字符串。
        """
        return self.indiMADict[periodName]

    def fetch_BBands_indicator(self,periodName):
        """ 外部接口API:布林带指标。通过周期字符串在移动平均线字典中查找。
            periodName: 周期名称的字符串。
        """
        return self.indiBBandsDict[periodName]

    def show_indicator(self,period,dataPicked):
        """ 内部接口API:指标图形绘制
            period:周期名称的字符串（用于计算蜡烛图展示根数）
            dataPicked:dateframe结构的数据。
            isDraw:是否展示图画的标志。对于后台运行模式默认不展示。
        """
        # 为降低系统负荷和增加实时性，对于零/小尺度周期的蜡烛图不再实时绘制
        indx = Constant.QUOTATION_DB_PREFIX.index(period)
        if Constant.SCALE_CANDLESTICK[indx] < Constant.DEFAULT_SCALE_CANDLESTICK_SHOW:
            return
        CandleStick.show_candlestick(dataPicked,self.indiMADict[period],self.indiBBandsDict[period],period)


