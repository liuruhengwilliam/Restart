#coding=utf-8
import datetime
import numpy as np
import pandas as pd
from pandas import DataFrame
from resource import Primitive
from resource import Constant
from resource import Configuration
from resource import Trace
import ClientNotify

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

        #按周期定义的策略区间格
        self.PeriodLattice = {}
        structType = np.dtype([('value',np.int16),('time',np.str_,40)])
        for period in Constant.QUOTATION_DB_PREFIX[1:-2]:
            value = Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(period)]
            structValue = [(0,' '),]*(3600*7*24/value)
            self.PeriodLattice.update({period:np.array(structValue,dtype=structType)})

    def get_lattice_map(self,period,time):
        """ 内部接口API: 获取特定周期的区间格参考信号
            返回值：numpy.array数组组合 -- 值+时间
            period: 周期字符串
            time: 时间字符串
        """
        ddTime = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
        weekday,hour,minute = int(ddTime.isoweekday()),int(ddTime.strftime("%H")),int(ddTime.strftime("%M"))
        if Constant.QUOTATION_DB_PREFIX.index(period) < Constant.QUOTATION_DB_PREFIX.index('1hour'):
            # 倍乘因子
            quotient = 3600/Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(period)]
            # 余数因子
            remainder = minute*60/Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(period)]
            return self.PeriodLattice[period][((weekday-1)*24+hour)*quotient + remainder]
        else:
            # 除数因子
            divisor = Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(period)]/3600
            return self.PeriodLattice[period][((weekday-1)*24+hour)/divisor]

    def set_lattice_map(self,period,time,value):
        """ 内部接口API: 设定特定周期的区间格参考信号
            period: 周期字符串
            time: 时间字符串
            value: 待设定模式值(int整型)
        """
        ddTime = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
        weekday,hour,minute = int(ddTime.isoweekday()),int(ddTime.strftime("%H")),int(ddTime.strftime("%M"))
        if Constant.QUOTATION_DB_PREFIX.index(period) < Constant.QUOTATION_DB_PREFIX.index('1hour'):
            # 倍乘因子
            quotient = 3600/Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(period)]
            # 余数因子
            remainder = minute*60/Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(period)]
            cursor = self.PeriodLattice[period][((weekday-1)*24+hour)*quotient + remainder]
            cursor['value'] = value
            cursor['time'] = time
        else:
            # 除数因子
            divisor = Constant.QUOTATION_DB_PERIOD[Constant.QUOTATION_DB_PREFIX.index(period)]/3600
            cursor = self.PeriodLattice[period][((weekday-1)*24+hour)/divisor]
            cursor['value'] = value
            cursor['time'] = time

    def update_lattice_map(self,period,serdf):
        """ 内部接口API: 更新指定周期的区间格参考信号映射位图
            period: 周期字符串
            serdf: 指定周期DataFrame数据
        """
        # 填充"区间格"。为后续计算多周期策略重叠区域做准备。
        prePolicyTime = ''
        for itemRow in serdf.itertuples():
            policyTime = itemRow[Constant.SER_DF_STRUCTURE.index('time')+1]
            if policyTime == prePolicyTime:#同一个时间点给出的策略不重复处理
                continue
            else:
                prePolicyTime = policyTime
            dfIndicator = serdf[serdf['time'] == policyTime]#找到若干个（大于等于一个）最新参考指示
            patternValSum = 0
            for timePoint in dfIndicator.itertuples():
                #累加K线组合模式值
                patternValSum += timePoint[Constant.SER_DF_STRUCTURE.index('patternVal')+1]
            self.set_lattice_map(period,policyTime,patternValSum)
        print self.PeriodLattice[period]

    def statistics_by_period(self,path,serData):
        """ 内部接口API：按交叉周期类型进行统计。
            path: 文件路径
            serData: 策略盈亏率数据字典--周期名字符串:DataFrame结构
        """
        recTime = ''
        F15M_30M = F30M_1H = F15M_1H = F15M_30M_1H = DataFrame(columns=Constant.SER_DF_STRUCTURE)
        #前提假定：小周期定时器给出策略条目的频率大于大周期定时器
        for itemRow in serData['15min'].itertuples():
            policyTime = itemRow[Constant.SER_DF_STRUCTURE.index('time')+1]
            if policyTime == recTime:#同一个时间点给出的策略不重复处理
                continue
            else:
                recTime = policyTime
            block15min = self.get_lattice_map('15min',policyTime)
            block15minVal = int(block15min['value'])
            block15minTime = block15min['time']

            block30min = self.get_lattice_map('30min',policyTime)
            block30minVal = int(block30min['value'])
            block30minTime = block30min['time']

            block1hour = self.get_lattice_map('1hour',policyTime)
            block1hourVal = int(block1hour['value'])
            block1hourTime = block1hour['time']

            if (block15minVal * block30minVal)>0:
                F15M_30M = pd.concat([F15M_30M,serData['15min'][serData['15min']['time'] == block15minTime]],ignore_index=True)
                F15M_30M = pd.concat([F15M_30M,serData['30min'][serData['30min']['time'] == block30minTime]],ignore_index=True)
                F15M_30M.to_csv(path+'15M-30M-ser.csv',sep=',',header=True)
            if (block15minVal * block1hourVal)>0:
                F15M_1H = pd.concat([F15M_1H,serData['15min'][serData['15min']['time'] == block15minTime]],ignore_index=True)
                F15M_1H = pd.concat([F15M_1H,serData['1hour'][serData['1hour']['time'] == block1hourTime]],ignore_index=True)
                F15M_1H.to_csv(path+'15M-1H-ser.csv',sep=',',header=True)
            if (block1hourVal * block30minVal)>0:
                F30M_1H = pd.concat([F30M_1H,serData['1hour'][serData['1hour']['time'] == block1hourTime]],ignore_index=True)
                F30M_1H = pd.concat([F30M_1H,serData['30min'][serData['30min']['time'] == block30minTime]],ignore_index=True)
                F30M_1H.to_csv(path+'30M-1H-ser.csv',sep=',',header=True)

            if (block15minVal * block30minVal)>0 and (block15minVal * block1hourVal)>0:
                # 多个dataframe数据叠加在一起
                F15M_30M_1H = pd.concat([F15M_30M_1H,serData['15min'][serData['15min']['time'] == block15minTime]],ignore_index=True)
                F15M_30M_1H = pd.concat([F15M_30M_1H,serData['30min'][serData['30min']['time'] == block30minTime]],ignore_index=True)
                F15M_30M_1H = pd.concat([F15M_30M_1H,serData['1hour'][serData['1hour']['time'] == block1hourTime]],ignore_index=True)
                F15M_30M_1H.to_csv(path+'15M-30M-1H-ser.csv',sep=',',header=True)

    def upate_afterwards_KLine_indicator(self,path):
        """ 外部接口API：从策略盈亏率数据库中提取K线组合模式的指标值并更新相应实例。
                       事后统计--依次截取数据库中每个条目。
            path: 文件路径
        """
        serData = {}
        for period in Constant.QUOTATION_DB_PREFIX[2:-2]:#前闭后开
            filename = Configuration.get_period_anyone_folder(path,period)+period+'-ser.db'
            tempDf = Primitive.translate_db_to_df(filename)

            # 填充字典。结构为"周期:DataFrame"
            serData.update({period:tempDf})
            # 更新区间格映射位图
            self.update_lattice_map(period,tempDf)

        # 进行交叉周期的分析统计
        self.statistics_by_period(path,serData)

    def draw_SERData_statistics(self,path):
        """ 外部接口API：策略盈亏率数据库的统计分析数据制图。
            path: 文件路径
        """
        DF15M_30M = Primitive.translate_csv_to_df(path+'15M-30M-ser.csv',Constant.SER_DF_STRUCTURE)
        DF30M_1H = Primitive.translate_csv_to_df(path+'30M-1H-ser.csv',Constant.SER_DF_STRUCTURE)
        DF15M_1H = Primitive.translate_csv_to_df(path+'15M-1H-ser.csv',Constant.SER_DF_STRUCTURE)
        DF15M_30M_1H = Primitive.translate_csv_to_df(path+'15M-30M-1H-ser.csv',Constant.SER_DF_STRUCTURE)


    def upate_realtime_KLine_indicator(self):
        """ 内部接口API：从策略盈亏率数据库中提取K线组合模式的指标值并更新相应实例。
                       实时更新--只需截取数据库中最后若干条目。
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


    def client_match(self):
        """
            外部接口API: 客户端程序驱动函数
            mode:调用者模式--realtime or afterwards
        """
        # 实时更新K线组合模式指示
        self.upate_realtime_KLine_indicator()

        # 更新其他各种指标指示

        # 匹配模式
        self.match_indicator()

        # 汇总各指标
        # self.actionDict中有非0项，需要将对应摘要说明字符串存档。
        for item in self.actionDict.iteritems():
            if item[1] != 0:
                ClientNotify.write_abstract(item[0],self.summaryDict[item[0]])

