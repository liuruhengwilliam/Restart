#coding=utf-8

from resource import Constant

import MA
import CandleStick
import BollingerBands
import DataProcess

class Indicator():
    """
        指标类。蜡烛图、移动平均线、布林带。
    """
    def __init__(self):
        self.ma = [0,]*len(Constant.MOVING_AVERAGE_LINE)
        self.BBands = [0,]*len(['upperBB','middleBB','lowerBB'])

    def process_indicator(self,periodName,dataWithId,isDraw=False):
        """ 外部接口API: 计算指标
            periodName:周期名称的字符串（用于计算蜡烛图展示根数）
            dataWithId:行情数据库中dateframe结构的数据。
        """
        dataPicked = DataProcess.process_quotes_drawing_candlestick(periodName,dataWithId)

        # 均线
        for index,tag in zip(range(len(Constant.MOVING_AVERAGE_LINE)),Constant.MOVING_AVERAGE_LINE):
            self.ma[index] = MA.compute_sma(dataPicked['close'].as_matrix(),tag)

        # 布林线
        self.BBands = BollingerBands.compute_BBands(dataPicked['close'].as_matrix())

        self.show_indicator(periodName,dataPicked,isDraw)

    def fetch_ma_indicator(self):
        """ 外部接口API:移动均线指标 """
        return self.ma

    def fetch_BBands_indicator(self):
        """ 外部接口API:布林带指标 """
        return self.BBands

    def show_indicator(self,periodName,dataPicked,isDraw=False):
        """ 内部接口API:指标图形绘制
            periodName:周期名称的字符串（用于计算蜡烛图展示根数）
            dataPicked:dateframe结构的数据。
            isDraw:是否展示图画的标志。对于后台运行模式默认不展示。
        """
        # 为降低系统负荷和增加实时性，对于零/小尺度周期的蜡烛图不再实时绘制
        indx = Constant.QUOTATION_DB_PREFIX.index(periodName)
        if isDraw==False and Constant.SCALE_CANDLESTICK[indx] < Constant.DEFAULT_SCALE_CANDLESTICK_SHOW:
            return
        CandleStick.show_candlestick(dataPicked,self.ma,self.BBands,periodName,isDraw)


