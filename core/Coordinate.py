#coding=utf-8

import os
import datetime
from resource import Trace
from resource import Configuration
from resource import Constant
from scrape import DataScrape
from indicator.Indicator import Indicator
from quotation import QuotationKit
from quotation.Quotation import *
from quotation.QuotationRecord import *
from strategy.Strategy import Strategy
from strategy import StrategyMisc
from strategy.ClientMatch import ClientMatch
from indicator import CandleStick

class Coordinate():
    """
        协作类:衔接“数据抓取”、“行情数据库”、“策略算法”模块，协同工作。
    """
    def __init__(self):
        # Quotation record Handle
        self.recordHdl = QuotationRecord()
        # Quotation DB Handle
        self.quoteHdl = Quotation(self.recordHdl)

        # 指标类初始化
        self.indicator = Indicator()
        # 策略类初始化
        self.strategy = Strategy()

        Trace.output('info', " ==== ==== Server Complete Initiation and Run Routine ==== ==== \n")

    # 以下是定时器回调函数:
    def work_heartbeat(self):
        """ 快速定时器(心跳定时器)回调函数 : 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数 """
        # 全球市场结算期间不更新缓冲记录
        # 数据抓取并筛选
        if Constant.is_closing_market():
            return

        infoList = DataScrape.query_info()
        if len(infoList) != 0:
            self.recordHdl.update_dict_record(infoList)

    def work_server_operation(self):
        """ 外部接口API: 服务器端某周期的处理回调函数。
            1.是否结算期及相关处理（转存csv文件和复位相关缓存）；2.更新行情数据库；
            3.行情数据转dateframe格式文件；4.绘制蜡烛图（若需要）；5.调用策略模块进行计算（若需要）
        """
        periodName = threading.currentThread().getName()
        markStart = datetime.datetime.now()

        #结算期间由更新标志控制不会多次更新
        if Constant.is_closing_market():
            self.recordHdl.reset_dict_record(periodName) #对应周期的行情记录缓存及标志复位
            return

        self.quoteHdl.update_quote(periodName) #更新行情数据

        #策略盈亏率数据库操作。先进行统计更新策略盈亏率数据，然后再分析及插入新条目。
        #5min周期定时器的主要任务就是更新盈亏率数据库。但5min行情数据必须周期刷新，所以update_quote(period)要前置。
        if periodName == '5min':
            recInfo = self.recordHdl.get_record_dict()['5min']
            self.strategy.update_strategy([recInfo['time'],float(recInfo['high']),float(recInfo['low'])])
            markEnd5min = datetime.datetime.now()
            Trace.output('info', "Period %s time out at %s and update strategy cost: %s\n"\
                         %(periodName, markStart, str(markEnd5min-markStart)))
            self.statistics_settlement()#统计汇总工作
            if Constant.is_weekend():
                os._exit(0) #退出Python程序
            return

        #其他周期定时器
        markQuote = datetime.datetime.now()
        Trace.output('info', "period %s update quote cost: %s"%(periodName,str(markQuote-markStart)))

        #指标计算和记录
        self.indicator.process_indicator(periodName,self.quoteHdl.query_quote(periodName))
        markIndicator = datetime.datetime.now()
        Trace.output('info', "period %s process indicator cost: %s"%(periodName,str(markIndicator-markQuote)))

        #策略算法计算
        #数据加工补全
        dataDealed = StrategyMisc.process_quotes_candlestick_pattern\
            (Configuration.get_period_working_folder(periodName),self.quoteHdl.query_quote(periodName))
        self.strategy.check_strategy(periodName,dataDealed)
        markStrategy = datetime.datetime.now()
        Trace.output('info', "period %s check strategy cost: %s\n"%(periodName,str(markStrategy-markIndicator)))

    def statistics_settlement(self):
        """内部接口API: 盈亏统计工作。由汇总各周期盈亏数据库生成表格文件。"""
        for tmName in Constant.QUOTATION_DB_PREFIX[1:]:
            path = Configuration.get_period_working_folder(tmName)
            if self.strategy.query_strategy_record(tmName) is not None:
                self.strategy.query_strategy_record(tmName).to_csv(path_or_buf=path+tmName+'-ser.csv',\
                                    columns=Constant.SER_DF_STRUCTURE, index=False)
            if self.quoteHdl.query_quote(tmName) is not None:
                self.quoteHdl.query_quote(tmName).to_csv(path_or_buf=path+tmName+'-quote.csv',\
                                    columns=['id',]+list(Constant.QUOTATION_STRUCTURE), index=False)
