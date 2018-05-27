#coding=utf-8

import re
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
        """ 外部函数API：抓取某股票代码的实时行情数据处理函数 """
        markStart = datetime.datetime.now()
        for target in self.recordHdl.get_target_list():
            # 通过正则表达式来区分标的类型：股票（数字） or 大宗商品（英文字母）
            # re.match(r'[a-zA-Z](.*)',target)#re.match在字符串开始处匹配模式
            if re.search(r'[^a-zA-Z]',target) is None:#大宗商品类型全是英文字母
                if Constant.is_futures_closed():
                    return
                infoList = DataScrape.query_info_futures()
                if len(infoList) != 2:
                    Trace.output('warn',"Faile to query:%s"%target)
                    continue
                # 更新record
                self.recordHdl.update_futures_record([target]+infoList)

            elif re.search(r'[^0-9](.*)',target) is None:#股票类型全是数字
                if Constant.is_stock_closed():
                    return
                quoteList = DataScrape.query_info_stock(target)
                if quoteList is None or len(quoteList) != len(Constant.QUOTATION_STRUCTURE):
                    Trace.output('warn',"Faile to query:%s"%target)
                    continue
                # 更新record
                self.recordHdl.update_stock_record([target]+quoteList)
            else:#错误类型
                Trace.output('warn',"ERROR target:%s"%target)
                continue

        markQuery = datetime.datetime.now()
        Trace.output('info', "It cost: %s to query stock(%s) from EastMoney."%\
                     (str(markQuery-markStart),' '.join(self.recordHdl.get_target_list())))

    def work_operation(self):
        """ 外部函数API：股票代码的周期行情数据缓存处理函数
            挂载在15min定时器。根据倍数关系，驱动更新其他大周期行情数据缓存。
        """
        markStart = datetime.datetime.now()
        year,week = markStart.strftime('%Y'),markStart.strftime('%U')
        for target in self.recordHdl.get_target_list():
            # 更新各周期行情数据缓存
            quoteGenerator = self.quoteHdl.update_quote(target)
            quoteDF = quoteGenerator.next()
            quoteDF.to_csv(Configuration.get_working_directory()+target+'-%s-%s-quote.csv'%(year,week),\
                            columns=['period',]+list(Constant.QUOTATION_STRUCTURE))

            # 按照时间次序排列，并删除开头的十一行（实时记录行）
            quoteDF = quoteDF.iloc[len(Constant.QUOTATION_DB_PERIOD):]

            # 各周期进行测验。若到期，则进行策略匹配。
            for index,period in enumerate(Constant.QUOTATION_DB_PREFIX[1:]):
                if self.quoteHdl.remainder_higher_order_tm(period)!=0:
                    continue

                # 策略盈亏率数据库操作。先进行统计更新策略盈亏率数据，然后再分析及插入新条目。
                # 5min周期定时器的主要任务就是更新盈亏率数据库。但5min行情数据必须周期刷新，所以update_quote(period)要前置。
                if period == '5min':
                    recInfo = self.recordHdl.get_record_dict(target)
                    self.strategy.update_strategy([recInfo['time'],recInfo['high'],recInfo['low']])
                    markEnd5min = datetime.datetime.now()
                    Trace.output('info', "As for %s,Period %s update strategy cost: %s\n"\
                             %(target, period, str(markEnd5min-markStart)))
                    continue

                # 指标计算和记录
                self.indicator.process_indicator(period,quoteDF[quoteDF['period'==period]])
                markIndicator = datetime.datetime.now()
                Trace.output('info', "As for %s,Period %s process indicator cost: %s"\
                             %(target, period, str(markIndicator-markStart)))

                # 策略算法计算
                # 数据加工补全
                dataDealed = StrategyMisc.process_quotes_candlestick_pattern\
                    (Configuration.get_period_working_folder(period),quoteDF[quoteDF['period'==period]])
                self.strategy.check_strategy(period,dataDealed)
                markStrategy = datetime.datetime.now()
                Trace.output('info', "As for %s,Period %s check strategy cost: %s\n"\
                             %(target, period, str(markStrategy-markIndicator)))

        # 基准定时器计数自增
        self.quoteHdl.increase_timeout_count()

        markEnd = datetime.datetime.now()
        Trace.output('info', "It cost %s to operate stock(%s) with timing out at %s."%\
                     (str(markEnd-markStart),' '.join(self.recordHdl.get_target_list())))

    def statistics_settlement(self):
        """内部接口API: 盈亏统计工作。由汇总各周期盈亏数据库生成表格文件。"""
        for tmName in Constant.QUOTATION_DB_PREFIX[Constant.QUOTATION_DB_PERIOD.index(Constant.UPDATE_BASE_PERIOD):]:
            path = Configuration.get_period_working_folder(tmName)
            if self.strategy.query_strategy_record(tmName) is not None:
                self.strategy.query_strategy_record(tmName).to_csv(path_or_buf=path+tmName+'-ser.csv',\
                                    columns=Constant.SER_DF_STRUCTURE, index=False)
            if self.quoteHdl.query_quote(tmName) is not None:
                self.quoteHdl.query_quote(tmName).to_csv(path_or_buf=path+tmName+'-quote.csv',\
                                    columns=['id',]+list(Constant.QUOTATION_STRUCTURE), index=False)
