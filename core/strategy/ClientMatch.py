#coding=utf-8
import datetime
import platform
if (platform.system() == "Linux"):#适配Linux系统下运行环境
    import matplotlib
    matplotlib.use("Pdf")
import matplotlib.pyplot as plt
import numpy as np
np.set_printoptions(suppress=True)
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
        # 四种指标指示记录字典
        self.actionDict = dict(zip(['KLine','MA','BBand','MACD'],[0,0,0,0]))
        # 四种指标指示摘要说明的字典
        self.summaryDict = dict(zip(['KLine','MA','BBand','MACD'],['','','','']))
        # 相关记录的字典--周期+DataFrame
        self.serDict = {}
        # 按周期定义的策略区间格字典--周期+位图数组（值，时间）
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

    def update_lattice_map(self,period,serDF):
        """ 内部接口API: 更新指定周期的区间格参考信号映射位图
            period: 周期字符串
            serdf: 指定周期DataFrame数据
        """
        # 填充"区间格"。为后续计算多周期策略重叠区域做准备。
        prePolicyTime = ''
        patternValSum = 0
        for itemRow in serDF.itertuples(index=False):
            curPolicyTime = itemRow[Constant.SER_DF_STRUCTURE.index('time')]
            if curPolicyTime == prePolicyTime:#同一个时间点给出的策略不重复处理
                #累加K线组合模式值
                patternValSum += itemRow[Constant.SER_DF_STRUCTURE.index('patternVal')]
            else:
                patternValSum = itemRow[Constant.SER_DF_STRUCTURE.index('patternVal')]
                prePolicyTime = curPolicyTime
            cursor = self.get_lattice_map(period,curPolicyTime)
            cursor['time'] = curPolicyTime
            cursor['value'] = patternValSum

        # 位图中的空白点使用前值进行填充
        preValue = 0
        preTime = ' '
        for item in self.PeriodLattice[period]:
            if item['value']==0 and item['time']==' ':# 空白点
                item['value'] = preValue
                item['time'] = preTime
            else:
                preValue = item['value']
                preTime = item['time']

    def upate_afterwards_KLine_indicator(self,path):
        """ 内部接口API：从策略盈亏率数据库中提取K线组合模式的指标值并更新相应实例。
                       事后统计--依次截取数据库中每个条目。
            path: 文件路径
        """
        for period in Constant.QUOTATION_DB_PREFIX[2:-2]:#前闭后开
            filename = Configuration.get_period_anyone_folder(path,period)+period+'-ser.db'
            tempDf = Primitive.translate_db_to_df(filename)

            # 填充字典。结构为"周期:DataFrame"
            self.serDict.update({period:tempDf})
            # 更新区间格映射位图
            self.update_lattice_map(period,tempDf)

    def statistics_M15M30H1_period(self,path):
        """ 内部接口API：按交叉周期类型进行统计。
            path: 文件路径
        """
        recTime = ''
        F15M_30M = F30M_1H = F15M_1H = F15M_30M_1H = DataFrame(columns=Constant.SER_DF_STRUCTURE)
        #前提假定：小周期定时器给出策略条目的频率大于大周期定时器
        for itemRow in self.serDict['15min'].itertuples(index=False):
            policyTime = itemRow[Constant.SER_DF_STRUCTURE.index('time')]
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
                F15M_30M = pd.concat([F15M_30M,self.serDict['15min'][self.serDict['15min']['time'] == block15minTime]],ignore_index=True)
                F15M_30M = pd.concat([F15M_30M,self.serDict['30min'][self.serDict['30min']['time'] == block30minTime]],ignore_index=True)
                F15M_30M.to_csv(path+'15M-30M-ser.csv',sep=',',header=True)
                self.serDict.update({'15min-30min':F15M_30M})
            if (block15minVal * block1hourVal)>0:
                F15M_1H = pd.concat([F15M_1H,self.serDict['15min'][self.serDict['15min']['time'] == block15minTime]],ignore_index=True)
                F15M_1H = pd.concat([F15M_1H,self.serDict['1hour'][self.serDict['1hour']['time'] == block1hourTime]],ignore_index=True)
                F15M_1H.to_csv(path+'15M-1H-ser.csv',sep=',',header=True)
                self.serDict.update({'15min-1hour':F15M_1H})
            if (block1hourVal * block30minVal)>0:
                F30M_1H = pd.concat([F30M_1H,self.serDict['1hour'][self.serDict['1hour']['time'] == block1hourTime]],ignore_index=True)
                F30M_1H = pd.concat([F30M_1H,self.serDict['30min'][self.serDict['30min']['time'] == block30minTime]],ignore_index=True)
                F30M_1H.to_csv(path+'30M-1H-ser.csv',sep=',',header=True)
                self.serDict.update({'30min-1hour':F30M_1H})
            if (block15minVal * block30minVal)>0 and (block15minVal * block1hourVal)>0:
                # 多个dataframe数据叠加在一起
                F15M_30M_1H = pd.concat([F15M_30M_1H,self.serDict['15min'][self.serDict['15min']['time'] == block15minTime]],ignore_index=True)
                F15M_30M_1H = pd.concat([F15M_30M_1H,self.serDict['30min'][self.serDict['30min']['time'] == block30minTime]],ignore_index=True)
                F15M_30M_1H = pd.concat([F15M_30M_1H,self.serDict['1hour'][self.serDict['1hour']['time'] == block1hourTime]],ignore_index=True)
                F15M_30M_1H.to_csv(path+'15M-30M-1H-ser.csv',sep=',',header=True)
                self.serDict.update({'15min-30min-1hour':F15M_30M_1H})

    def filter_trash_item(self,period,serDataTag):
        """ 内部接口：去除干扰项。某周期下同一时刻会生成多条矛盾条目，剔除弱势一方
            返回值：过滤后的DataFrame类型数据。某周期下一个时刻只保留一个条目
            period：周期名称字符串
            serDataTag: 字典项的键值--字符串
        """
        recTime = ''
        filterDF = None
        serData = self.serDict[serDataTag][self.serDict[serDataTag]['tmName']=='15min']

        for indx in range(len(serData)):
            patternVal = serData.iloc[indx]['patternVal']
            policyTime = serData.iloc[indx]['time']
            latticeVal = self.get_lattice_map(period,policyTime)['value']

            #从数据源中剔除同一个时间点的冗余策略条目或者与位图映射值不符的策略条目（干扰条目）
            if policyTime != recTime and int(latticeVal*patternVal) > 0:
                if filterDF is None:
                    filterDF = DataFrame([serData.iloc[indx]])#用Series填充DataFrame结构
                else:
                    filterDF = filterDF.append([serData.iloc[indx]],ignore_index=True)
                recTime = policyTime

        return filterDF

    def calculate_rate(self,dataDF):
        """ 内部接口API: 计算盈亏比率。
            返回值: 盈亏百分比的numpy.array结构。
            dataDF: DataFrame结构数据
        """
        # 盈亏列表的字典
        retDict = {}
        # 字符串的numpy.ndarray结构，策略方向
        patternVal = dataDF["patternVal"].as_matrix()

        # 获取方向因子
        direction = patternVal.astype(int)/np.abs(patternVal.astype(int))

        # basePrice: 字符串的numpy.ndarray结构，策略给出时的基准价格
        basePrice = dataDF["price"].as_matrix()

        # earnPrice/lossPrice: 字符串的numpy.ndarray结构，某周期内的极值价格
        for tag in Constant.SER_DF_STRUCTURE[7:-2:4]:
            earnPrice = dataDF[tag].as_matrix()
            # 价格差值
            earnDelta = earnPrice.astype(float) - basePrice.astype(float)
            # 盈亏百分比--相对于basePrice
            retDict.update({tag:earnDelta*direction*100/basePrice.astype(float)})

        for tag in Constant.SER_DF_STRUCTURE[9:-2:4]:
            lossPrice = dataDF[tag].as_matrix()
            lossDelta = lossPrice.astype(float) - basePrice.astype(float)
            retDict.update({tag:lossDelta*direction*100/basePrice.astype(float)})

        # 过滤比率异常的数据点
        for key,list in retDict.items():
            for item in list:
                if abs(item) > Constant.STOP_LOSS_RATE*100:# 大于10%的比率记为异常比率
                    retDict[key][retDict[key].tolist().index(item)]=0
                    Trace.output('warn',"change key:"+key+" value:%d"%item)
        return retDict

    def draw_statistics(self,dataDict):
        """ 外部接口API：策略盈亏率数据库的统计分析数据制图。
            dataDict: 策略的盈利字典项
        """
        # X轴有7个刻度：15min/30min/1hour/2hour/4hour/6hour/12hour
        # Y轴为盈利比率。有正有负
        rate15MEarn = dataDict['M15maxEarn']
        rate30MEarn = dataDict['M30maxEarn']
        rate1HEarn = dataDict['H1maxEarn']
        rate2HEarn = dataDict['H2maxEarn']
        rate4HEarn = dataDict['H4maxEarn']
        rate6HEarn = dataDict['H6maxEarn']
        rate12HEarn = dataDict['H12maxEarn']
        rate15MLoss = dataDict['M15maxLoss']
        rate30MLoss = dataDict['M30maxLoss']
        rate1HLoss = dataDict['H1maxLoss']
        rate2HLoss = dataDict['H2maxLoss']
        rate4HLoss = dataDict['H4maxLoss']
        rate6HLoss = dataDict['H6maxLoss']
        rate12HLoss = dataDict['H12maxLoss']

        plt.plot(rate15MEarn,'cx--')
        plt.show()

    def research_statistics(self,path):
        """ 外部接口API：策略盈亏率数据库的统计分析数据展示。
            path: 文件路径
        """
        # 填充字典项:策略盈亏周期字典，策略方向周期位图字典
        self.upate_afterwards_KLine_indicator(path)
        # M15 M30 H1周期的同向时间点条目汇总--以下操作基于这些交叉周期
        self.statistics_M15M30H1_period(path)
        # 过滤数据(同向中的干扰条目，即弱势项)--提纯操作
        pureDf = self.filter_trash_item('15min','15min-30min-1hour')
        # 计算盈亏比率
        rateDict = self.calculate_rate(pureDf)
        # 制图
        self.draw_statistics(rateDict)

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

