#coding=utf-8

import os
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
from resource import Constant
from resource import Configuration
from resource import Trace
from strategy.Strategy import Strategy
from strategy.Strategy import StrategyMisc

class Statistics():
    """ 各种方案匹配搜索类
        各周期的匹配搜索实例包含：K线组合信号、MA趋势、BBand支撑/压力值、MACD指示信号
    """
    def __init__(self,path):
        """ 初始化相关指标各周期的实例
            path:数据文件存储目录（可能为服务程序的工作目录）。即客户端程序的依赖目录。
        """
        self.path = path
        self.targetList = Configuration.parse_target_list(path+'Properties.xml')
        self.strategyIns = Strategy(self.targetList)
        self.KLineIndicator = dict(zip(Constant.QUOTATION_DB_PREFIX[1:-2],[0]*len(Constant.QUOTATION_DB_PREFIX[1:-2])))
        self.BBandIndicator = {}
        self.MAIndicator = {}
        self.MACDIndicator = {}
        # 四种指标指示记录字典
        self.actionDict = dict(zip(['KLine','MA','BBand','MACD'],[0,0,0,0]))
        # 四种指标指示摘要说明的字典
        self.summaryDict = dict(zip(['KLine','MA','BBand','MACD'],['','','','']))
        # 行情数据的记录字典--周期+DataFrame
        self.quoteDict = {}
        # 策略盈亏的记录字典--周期+DataFrame
        self.serDict = {}
        # 按周期定义的策略区间格字典--周期+位图数组（值，时间）
        self.PeriodLattice = {}
        self.reset_relevant_dict()

    def reset_relevant_dict(self):
        """ 内部接口API: 复位相关字典项 """
        # 行情数据的记录字典--周期+DataFrame
        self.quoteDict = {}
        # 策略盈亏的记录字典--周期+DataFrame
        self.serDict = {}
        # 按周期定义的策略区间格字典--周期+位图数组（值，时间）
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

    def count_cross_M15M30H1_period(self,target):
        """ 内部接口API：按交叉周期类型进行统计。
        """
        recTime = ''
        F15M_30M = F30M_1H = F15M_1H = F15M_30M_1H = DataFrame(columns=Constant.SER_DF_STRUCTURE)
        self.serDict.update({'15min-30min':F15M_30M})
        self.serDict.update({'30min-1hour':F30M_1H})
        self.serDict.update({'15min-1hour':F15M_1H})
        self.serDict.update({'15min-30min-1hour':F15M_30M_1H})

        #前提假定：小周期定时器给出策略条目的频率大于大周期定时器
        #最小周期是15min的交叉匹配
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
                F15M_30M.to_csv(self.path+'%s-15M-30M-ser.csv'%target,sep=',',header=True)
                self.serDict.update({'15min-30min':F15M_30M})
            if (block15minVal * block1hourVal)>0:
                F15M_1H = pd.concat([F15M_1H,self.serDict['15min'][self.serDict['15min']['time'] == block15minTime]],ignore_index=True)
                F15M_1H = pd.concat([F15M_1H,self.serDict['1hour'][self.serDict['1hour']['time'] == block1hourTime]],ignore_index=True)
                F15M_1H.to_csv(self.path+'%s-15M-1H-ser.csv'%target,sep=',',header=True)
                self.serDict.update({'15min-1hour':F15M_1H})
            if (block15minVal * block30minVal)>0 and (block15minVal * block1hourVal)>0:
                # 多个dataframe数据叠加在一起
                F15M_30M_1H = pd.concat([F15M_30M_1H,self.serDict['15min'][self.serDict['15min']['time'] == block15minTime]],ignore_index=True)
                F15M_30M_1H = pd.concat([F15M_30M_1H,self.serDict['30min'][self.serDict['30min']['time'] == block30minTime]],ignore_index=True)
                F15M_30M_1H = pd.concat([F15M_30M_1H,self.serDict['1hour'][self.serDict['1hour']['time'] == block1hourTime]],ignore_index=True)
                F15M_30M_1H.to_csv(self.path+'%s-15M-30M-1H-ser.csv'%target,sep=',',header=True)
                self.serDict.update({'15min-30min-1hour':F15M_30M_1H})

        #最小周期是30min的交叉匹配
        recTime = ''
        for itemRow in self.serDict['30min'].itertuples(index=False):
            policyTime = itemRow[Constant.SER_DF_STRUCTURE.index('time')]
            if policyTime == recTime:#同一个时间点给出的策略不重复处理
                continue
            else:
                recTime = policyTime
            block30min = self.get_lattice_map('30min',policyTime)
            block30minVal = int(block30min['value'])
            block30minTime = block30min['time']

            block1hour = self.get_lattice_map('1hour',policyTime)
            block1hourVal = int(block1hour['value'])
            block1hourTime = block1hour['time']
            if (block1hourVal * block30minVal)>0:
                F30M_1H = pd.concat([F30M_1H,self.serDict['30min'][self.serDict['30min']['time'] == block30minTime]],ignore_index=True)
                F30M_1H = pd.concat([F30M_1H,self.serDict['1hour'][self.serDict['1hour']['time'] == block1hourTime]],ignore_index=True)
                F30M_1H.to_csv(self.path+'%s-30M-1H-ser.csv'%target,sep=',',header=True)
                self.serDict.update({'30min-1hour':F30M_1H})

    def pickup_pure_item(self,period,serDataTag):
        """ 内部接口：去除干扰项。某周期下同一时刻会生成多条矛盾条目，剔除弱势一方
            返回值：过滤后的DataFrame类型数据。某周期下一个时刻只保留一个条目
            period：周期名称字符串
            serDataTag: 字典项的键值--字符串
        """
        recTime = ''
        filterDF = None
        serData = self.serDict[serDataTag][self.serDict[serDataTag]['period']==period]

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

    def filter_time_phase_item(self,dataDF,ruler):
        """ 内部接口：依据不同时段来过滤条目。
            返回值：过滤后的DataFrame类型数据。
            dataDF：DataFrame结构数据
            ruler: 过滤规则的时间字符串
        """
        retDF = None
        for indx in range(len(dataDF)):
            policyTime = dataDF.iloc[indx]['time']
            baseTimeDT = datetime.datetime.strptime(policyTime,"%Y-%m-%d %H:%M:%S")
            rulerTmBegin = policyTime.split(" ")[0]+" "+Constant.TIME_SEGMENT_DICT[ruler][0]
            rulerTmEnd = policyTime.split(" ")[0]+" "+Constant.TIME_SEGMENT_DICT[ruler][1]
            rulerTimeBeginDT = datetime.datetime.strptime(rulerTmBegin,"%Y-%m-%d %H:%M:%S")
            rulerTimeEndDT = datetime.datetime.strptime(rulerTmEnd,"%Y-%m-%d %H:%M:%S")

            # 累积介于该ruler时间段中间的条目
            if baseTimeDT >= rulerTimeBeginDT and baseTimeDT <= rulerTimeEndDT:
                if retDF is None:
                    retDF = DataFrame([dataDF.iloc[indx]])#用Series填充DataFrame结构
                else:
                    retDF = retDF.append([dataDF.iloc[indx]],ignore_index=True)

        return retDF

    def calculate_profit_rate(self,dataDF):
        """ 内部接口API: 计算盈亏比率。
            返回值: 盈亏百分比的DataFrame结构。
            dataDF: DataFrame结构数据
        """
        # 盈亏列表的字典
        retDict = {}
        clmn = []
        # 字符串的numpy.ndarray结构，策略方向
        patternVal = dataDF["patternVal"].as_matrix()

        # 获取方向因子
        direction = patternVal.astype(int)/np.abs(patternVal.astype(int))

        # basePrice: 字符串的numpy.ndarray结构，策略给出时的基准价格
        basePrice = dataDF["price"].as_matrix()

        # earnPrice/lossPrice: 字符串的numpy.ndarray结构，某周期内的极值价格
        for tag in Constant.SER_DF_STRUCTURE[Constant.SER_DF_STRUCTURE.index('M15maxEarn'):-2:2]:
            clmn.append(tag)
            if tag.find('Earn'):
                earnPrice = dataDF[tag].as_matrix()
                # 价格差值
                earnDelta = earnPrice.astype(float) - basePrice.astype(float)
                # 盈亏百分比--相对于basePrice
                retDict.update({tag:earnDelta*direction*100/basePrice.astype(float)})
            else:
                lossPrice = dataDF[tag].as_matrix()
                lossDelta = lossPrice.astype(float) - basePrice.astype(float)
                retDict.update({tag:lossDelta*direction*100/basePrice.astype(float)})

        # 过滤比率异常的数据点
        for key,list in retDict.items():
            for item in list:
                if abs(item) > Constant.STOP_LOSS_RATE*100:# 大于10%的比率记为异常比率
                    retDict[key][retDict[key].tolist().index(item)]=0
                    Trace.output('warn',"change key:"+key+" value:%d"%item)
        return pd.DataFrame(retDict,columns=clmn)

    def calculate_time_cost_on_peak(self,dataDF):
        """ 内部接口API: 计算策略各周期下出现极值的耗时。
            返回值: 各周期极值的耗时DataFrame结构。
            dataDF: DataFrame结构数据
        """
        timeDict = {}
        clmn = []

        # 转换极值时间列字符串为Datetime结构。[0:16]----刨去秒计时。
        for tag in Constant.SER_DF_STRUCTURE[Constant.SER_DF_STRUCTURE.index('M15maxEarnTime'):-2:2]:
            cacheList = []
            clmn.append(tag)
            for row in dataDF.itertuples(index=False):
                # 转换策略给出时间的字符串为Datetime结构。
                baseTimeDT = datetime.datetime.strptime(row[Constant.SER_DF_STRUCTURE.index('time')],"%Y-%m-%d %H:%M:%S")
                tm = row[Constant.SER_DF_STRUCTURE.index(tag)]
                if tm == '':# 没有时间记录
                    deltaTm = 0
                else:
                    if len(tm.split(':')) == 2:
                        tagDT = datetime.datetime.strptime(tm,"%Y-%m-%d %H:%M")
                    else:
                        tagDT = datetime.datetime.strptime(tm,"%Y-%m-%d %H:%M:%S")
                    deltaTm = (tagDT-baseTimeDT).total_seconds()

                cacheList.append(deltaTm)

            timeDict.update({tag:cacheList})

        return pd.DataFrame(timeDict,columns=clmn)

    def draw_statistics(self,tag,rateDF,deltaTmDF):
        """ 内部接口API：策略盈亏率数据库的统计分析数据制图。
                    为了将所有数据绘制在一张图中，采用X轴为比率值，Y轴为时间周期（固定数目）
            rateDF: 策略盈利比率的DataFrame结构数据
            deltaTmDF: 策略盈利极值时间的DataFrame结构数据
        """
        plt.figure(figsize=(16,10))
        #plt.grid(True)
        plt.xlabel("Time")
        plt.ylabel("Rate")

        # X轴的尺度设定为24个单位
        x_scale = 24
        # X轴设置7个刻度
        x = ['0','H2','H4','H6','H8','H10','H12','H14','H16','H18','H20','H22']
        plt.xticks(range(0,x_scale,2),x)
        # Y轴为盈利比率。有正有负
        rateEarnDF = rateDF.ix[:,Constant.SER_DF_STRUCTURE[Constant.SER_DF_STRUCTURE.index('M15maxEarn'):-2:4]]
        rateLossDF = rateDF.ix[:,Constant.SER_DF_STRUCTURE[Constant.SER_DF_STRUCTURE.index('M15maxLoss'):-2:4]]
        plt.title(tag+" Rate based on Time-Cost")
        #   Period     Earn marker styles          Loss marker styles      Color
        #  15Minute  >(Triangle right marker)    <(Triangle left marker)   blue
        #  30Minute  ^(Triangle up marker)       v(Triangle down marker)   magenta
        #  1Hour     4(Tripod right marker)      3(Triangle left marker)    red
        #  2Hour     2(Tripod up marker)         1(Tripod down marker)      cyan
        #  4Hour     o(Circle marker)            s(Square marker)           green
        #  6Hour     p(Pentagon marker)          h(Hexagon marker)          yellow
        #  12Hour    d(Thin diamond marker)      *(Star marker)            undefine
        plt.plot(deltaTmDF.ix[:,'M15maxEarnTime']/3600,rateEarnDF['M15maxEarn'].as_matrix(),'b>',label="M15")
        plt.plot(deltaTmDF.ix[:,'M15maxLossTime']/3600,rateLossDF['M15maxLoss'].as_matrix(),'b<')
        plt.plot(deltaTmDF.ix[:,'M30maxEarnTime']/3600,rateEarnDF['M30maxEarn'].as_matrix(),'m^',label="M30")
        plt.plot(deltaTmDF.ix[:,'M30maxLossTime']/3600,rateLossDF['M30maxLoss'].as_matrix(),'mv')
        plt.plot(deltaTmDF.ix[:,'H1maxEarnTime']/3600,rateEarnDF['H1maxEarn'].as_matrix(),'r4',label="H1")
        plt.plot(deltaTmDF.ix[:,'H1maxLossTime']/3600,rateLossDF['H1maxLoss'].as_matrix(),'r3')
        plt.plot(deltaTmDF.ix[:,'H2maxEarnTime']/3600,rateEarnDF['H2maxEarn'].as_matrix(),'c2',label="H2")
        plt.plot(deltaTmDF.ix[:,'H2maxLossTime']/3600,rateLossDF['H2maxLoss'].as_matrix(),'c1')
        plt.plot(deltaTmDF.ix[:,'H4maxEarnTime']/3600,rateEarnDF['H4maxEarn'].as_matrix(),'go',label="H4")
        plt.plot(deltaTmDF.ix[:,'H4maxLossTime']/3600,rateLossDF['H4maxLoss'].as_matrix(),'gs')
        plt.plot(deltaTmDF.ix[:,'H6maxEarnTime']/3600,rateEarnDF['H6maxEarn'].as_matrix(),'yp',label="H6")
        plt.plot(deltaTmDF.ix[:,'H6maxLossTime']/3600,rateLossDF['H6maxLoss'].as_matrix(),'yh')
        plt.legend()
        plt.savefig('%s%s_%s.png'%(self.path,tag,datetime.datetime.now().strftime("%Y-%m-%d")),dpi=200)
        #plt.show()

    def analyse_ser_data_in_history(self,target):
        """ 外部接口API：策略盈亏率数据库的统计分析数据展示。
        """
        serFile = self.path+'%s-ser.csv'%target
        if not os.path.exists(serFile):
            Trace.output('fatal','LEAK FOR %s ser.csv FILE'%target)
            return

        serDF = pd.read_csv(serFile)
        # 填充字典项:策略盈亏周期字典，策略方向周期位图字典
        for period in Constant.QUOTATION_DB_PREFIX[2:-2]:#前闭后开
            tmpDf = serDF[serDF['period']==period]
            if len(tmpDf) == 0:
                tmpDf = DataFrame(columns=Constant.SER_DF_STRUCTURE)#建立空的DataFrame数据结构
            # 填充字典。结构为"周期:DataFrame"
            self.serDict.update({period:tmpDf})
            # 更新区间格映射位图
            self.update_lattice_map(period,tmpDf)

    def analyse_quote_data_in_history(self,target):
        """ 内部接口API：从策略盈亏率数据库中提取K线组合模式的指标值并更新相应实例。
                       实时更新--只需截取数据库中最后若干条目。
            说明：暂时只考虑15min/30min/1hour
        """
        quoteFile = self.path+'%s-quote.csv'%target
        if not os.path.exists(quoteFile):
            Trace.output('fatal','LEAK FOR %s quote.csv FILE'%target)
            return

        quoteDF = pd.read_csv(quoteFile)
        for period in Constant.QUOTATION_DB_PREFIX[2:-2]:#前闭后开
            tmpDf = quoteDF[quoteDF['period']==period]
            self.quoteDict.update({period:tmpDf})

            # 模式匹配
            subsetDF = None
            for indx in range(len(self.quoteDict[period])):
                if subsetDF is None:
                    subsetDF = self.quoteDict[period].iloc[indx:indx+1]
                else:
                    subsetDF = subsetDF.append(self.quoteDict[period].iloc[indx:indx+1])
                dataDealed = StrategyMisc.process_quotes_candlestick_pattern(subsetDF)
                # 逐条进行匹配
                self.strategyIns.check_strategy(period,dataDealed)

        # 更新策略条目的极值
        quoteM5 = quoteDF[quoteDF['period']=='5min']
        for item in quoteM5.itertuples(index=False):
            self.strategyIns.update_strategy([datetime.datetime.strptime(item[1],\
                                '%Y-%m-%d %H:%M:%S'),float(item[3]),float(item[4])])

        for period in Constant.QUOTATION_DB_PREFIX[2:-2]:#前闭后开
            # 填充字典。结构为"周期:DataFrame"
            self.serDict.update({period:self.strategyIns.query_strategy_record(period)})
            # 更新区间格映射位图
            self.update_lattice_map(period,self.strategyIns.query_strategy_record(period))

    def match_KLineIndicator(self):
        """ 外部接口API: K线指标组合模式 """
        for target in self.targetList:
            if not os.path.exists(self.path+'%s-ser.csv'%target):
                # 从行情数据库中提取并匹配策略组合模式，生成策略盈亏数据
                self.analyse_quote_data_in_history(target)
            else:
                self.analyse_ser_data_in_history(target)

            # M15 M30 H1周期的同向时间点条目汇总--以下操作基于这些交叉周期
            self.count_cross_M15M30H1_period(target)

            for mixTag in ['15min-30min','15min-1hour','15min-30min-1hour']:
                # 过滤数据(同向中的干扰条目，即弱势项)--提纯操作
                pureDf = self.pickup_pure_item('15min',mixTag)
                print 'Pure DataFrame\n',pureDf#调试点
                if pureDf is None:
                    continue
                for ruler in ["Gold_saint","Silver_saint","Copper_saint"]:
                    # 依据时间段提取条目
                    filterDf = self.filter_time_phase_item(pureDf,ruler)
                    if filterDf is None:
                        continue
                    # 计算盈亏比率
                    rateDF = self.calculate_profit_rate(filterDf)
                    print 'Rate DataFrame\n',rateDF#调试点
                    # 计算时间差值
                    deltaTimeDF = self.calculate_time_cost_on_peak(filterDf)
                    print 'delta Time DataFrame\n',deltaTimeDF#调试点
                    # 制图
                    self.draw_statistics(target+mixTag+ruler,rateDF,deltaTimeDF)

            self.reset_relevant_dict()

    def statistics_operation(self):
        """ 外部接口API:分析线程的主处理函数。 """
        if Constant.be_closed(self.targetList[0])==True and Constant.be_exited(self.targetList[0])==False:
            # 在闭市和程序退出时间差(30min)中有且仅有一次定时器到期，相关数据文件打包
            zipName = '-'.join(self.targetList)+datetime.datetime.now().strftime('-%m-%d')+'.zip'
            Configuration.zip_data_statistics_file(zipName,self.path)
            # 发送电子邮件
            Configuration.send_notification_email(zipName,' '.join(self.targetList),\
                                    [Configuration.get_current_directory()+zipName])

        if Constant.be_exited(self.targetList[0]):
            os._exit(0)
        self.match_KLineIndicator()
