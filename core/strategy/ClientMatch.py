#coding=utf-8

from pandas import Series,DataFrame
from resource import Primitive
from resource import Constant
from resource import Configuration

class ClientMatch():
    """ 各种方案匹配搜索类
        各周期的匹配搜索实例包含：K线组合信号、MA趋势、BBand支撑/压力值、MACD指示信号
    """
    def __init__(self):
        """ 初始化相关指标各周期的实例 """
        self.KLineIndicator = dict(zip(Constant.QUOTATION_DB_PREFIX[1:-2],[0]*len(Constant.QUOTATION_DB_PREFIX[1:-2])))
        self.MACDIndicator = {}
        self.MAIndicator = {}
        self.MACDIndicator = {}

    def get_indicator(self,indicator,period):
        """ 外部接口API: 获取特定指标的某周期参考信号
            indicator: 特定指标的字符串描述符
            period: 周期字符串
        """
        if indicator == 'KLine':
            return self.KLineIndicator[period]

        return None

    def set_indicator(self,indicator,period,value):
        """ 外部接口API: 设定特定指标的某周期参考信号
            indicator: 特定指标的字符串描述符
            period: 周期字符串
            value: 参考信号值--后续对于其他类型指标可能有异构情况
        """
        if indicator == 'KLine':
            self.KLineIndicator[period] = value

    def parse_ser_db(self):
        """ 外部接口API：分析策略盈亏率数据库 """
        for period in Constant.QUOTATION_DB_PREFIX[1:-2]:
            filename = Configuration.get_period_working_folder(period)+period+'-ser.db'
            serData = Primitive.translate_db_to_df(filename)
            length = len(serData)
            if length == 0:
                continue
            lastSerItem = serData.ix[length-1:,['time']]#获取最后一个条目
            latestIndicatorTm = str(lastSerItem.values).strip('[u\']')#提取最新参考指示的给出时间点
            latestIndicator = serData[serData['time'] == latestIndicatorTm]#找到若干个最新参考指示

