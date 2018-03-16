#coding=utf-8

import numpy as np
from pandas import DataFrame
from resource import Primitive
from resource import Constant
from resource import Configuration
from resource import Trace

class ClientMatch():
    """ 各种方案匹配搜索类
        各周期的匹配搜索实例包含：K线组合信号、MA趋势、BBand支撑/压力值、MACD指示信号
    """
    def __init__(self):
        """ 初始化相关指标各周期的实例 """
        self.KLineIndicator = dict(zip(Constant.QUOTATION_DB_PREFIX[1:-2],[0]*len(Constant.QUOTATION_DB_PREFIX[1:-2])))
        self.BBandIndicator = {}
        self.MAIndicator = {}
        self.MACDIndicator = {}
        #四种指标指示记录字典
        self.actionDict = dict(zip(['KLine','MA','BBand','MACD'],[0,0,0,0]))
        #四种指标指示摘要说明的字典
        self.summaryDict = dict(zip(['KLine','MA','BBand','MACD'],['','','','']))

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

    def upate_KLine_indicator(self):
        """ 内部接口API：从策略盈亏率数据库中提取K线组合模式的指标值并更新相应实例
            说明：暂时只考虑15min/30min/1hour
        """
        # 清空摘要说明
        self.summaryDict['KLine']=''
        for period in Constant.QUOTATION_DB_PREFIX[2:5]:#前闭后开
            filename = Configuration.get_period_working_folder(period)+period+'-ser.db'
            serData = Primitive.translate_db_to_df(filename)
            if len(serData) == 0:#没有生成的条目就略过
                continue

            lastSerItem = serData.ix[len(serData)-1:,['time']]#获取最后一个条目
            latestIndicatorTm = str(lastSerItem.values).strip('[u\']')#提取最新参考指示的给出时间点
            dfLatestIndicator = serData[serData['time'] == latestIndicatorTm]#找到若干个最新参考指示

            patternValSum = 0
            for itemRow in dfLatestIndicator.itertuples():
                #累加K线组合模式值
                patternValSum += itemRow[Constant.SER_DF_STRUCTURE.index('patternVal')+1]

                #拼装摘要说明
                record = np.array(itemRow).tolist()[Constant.SER_DF_STRUCTURE.index('indx')+2:\
                                                    Constant.SER_DF_STRUCTURE.index('patternVal')+2]
                self.summaryDict['KLine']='%s%s\n'%(self.summaryDict['KLine'],' '.join(record).replace('u\'',''))

            self.KLineIndicator[period] = patternValSum#更新对应实例值

    def match_indicator(self):
        """ 内部接口API: 综合考虑各种指标，给出指示 """
        # K线组合模式
        period1, period2, period3 = Constant.QUOTATION_DB_PREFIX[2:5]#前闭后开
        if self.KLineIndicator[period1]>0 and self.KLineIndicator[period2]>0 and self.KLineIndicator[period3]>0:
            self.actionDict['KLine'] = 1
        elif self.KLineIndicator[period1]<0 and self.KLineIndicator[period2]<0 and self.KLineIndicator[period3]<0:
            self.actionDict['KLine'] = -1
        else:
            self.actionDict['KLine'] = 0

        # MA趋势

        # BBand支撑/压力值

        # MACD指示信号


    def client_motor(self):
        """ 外部接口API: 客户端程序驱动函数 """
        # 更新K线组合模式指示
        self.upate_KLine_indicator()

        # 更新其他各种指标指示

        # 匹配模式
        self.match_indicator()

        # 汇总各指标
        # self.actionDict中有非0项，需要将对应摘要说明字符串存档。
        for item in self.actionDict.iteritems():
            if item[1] != 0:
                self.write_abstract(item[0],self.summaryDict[item[0]])

    def write_abstract(self,indicator,strAbstract):
        """ 内部接口API: 各指标的指示摘要说明字符串存档函数
            strAbstract: 待写入的摘要字符串
        """
        filePath = Configuration.get_working_directory()+'abstract.txt'

        fd = open(filePath,'a+')
        fd.write(Constant.ABSTRACT_TITLE[indicator])
        if indicator == 'KLine':
            fd.write(' %s'%self.actionDict[indicator])
            # 对于别的指标，可写入其他信息：MA--趋势；MACD--金叉/死叉；BBand--压力/支撑位等

        fd.write('\n')
        fd.write(strAbstract)
        fd.close()

    def read_abstract(self):
        """ 内部接口API: 各指标的指示摘要说明字符串读档函数 """

