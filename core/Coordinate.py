#coding=utf-8

import os
import datetime
import urllib
from resource import Trace
from resource import Configuration
from resource import Constant
from resource import ExceptDeal
from resource import Primitive
from scrape import DataScrape
from indicator.Indicator import Indicator
from quotation import QuotationKit
from quotation.QuotationDB import *
from quotation.QuotationRecord import *
from strategy.Strategy import Strategy
from strategy import StratEarnRate
from strategy import Decision
from indicator import CandleStick

class Coordinate():
    """
        协作类:衔接“数据抓取”、“行情数据库”、“策略算法”模块，协同工作。
    """
    def __init__(self,role):
        self.week = (datetime.datetime.now()).strftime('%U')#本周周数记录

        if role == 'Client':
            return
        # Quotation record Handle
        self.recordHdl = QuotationRecord(Constant.UPDATE_PERIOD_FLAG)
        self.recordDict = self.recordHdl.get_record_dict()
        # Quotation DB Handle
        self.dbQuotationHdl = QuotationDB(Constant.UPDATE_PERIOD_FLAG,self.recordDict)

        # 指标类初始化
        self.indicator = Indicator()

        # 策略类初始化
        self.strategy = Strategy()
        Trace.output('info', " ==== ==== %s Complete Initiation and Run Routine ==== ==== \n"%role)

    # 以下是定时器回调函数:
    def work_heartbeat(self):
        """ 快速定时器(心跳定时器)回调函数 : 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数 """
        # 全球市场结算期间不更新缓冲记录
        # 数据抓取并筛选
        if Constant.is_closing_market():
            self.statistics_settlement()
            return

        infoList = DataScrape.query_info()
        if len(infoList) != 0:
            self.recordHdl.update_dict_record(infoList)

        if Constant.exit_on_weekend(self.week):#此时处理所有周期的相关内容
            self.statistics_settlement()
            os._exit(0) #退出Python程序

    def work_client_operation(self):
        """ 外部接口API: 客户端线程回调函数 """
        if Constant.is_closing_market():
            Configuration.download_statistic_file('csv')

        Trace.output('info', "client work on "+str(datetime.datetime.now()))
        #下载各周期的db文件
        for item in ("quote","ser"):
            Configuration.download_realtime_file(item)

        for tmName in Constant.QUOTATION_DB_PREFIX[2:-3]:
            dataWithId = Primitive.translate_db_to_df('%s%s-quote.db'\
                            %(Configuration.get_period_working_folder(tmName),tmName))
            CandleStick.manual_show_candlestick(tmName,dataWithId)

        #筛选条目，最大程度匹配策略


        #屏幕弹框(发送消息及email--应包含策略条目详情)


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

        self.dbQuotationHdl.update_quote(periodName) #更新行情数据

        #策略盈亏率数据库操作。先进行统计更新策略盈亏率数据，然后再分析及插入新条目。
        #5min周期定时器的主要任务就是更新盈亏率数据库。但5min行情数据必须周期刷新，所以update_quote(period)要前置。
        if periodName == '5min':
            recInfo = self.recordHdl.get_record_dict()['5min']
            self.strategy.update_strategy([recInfo['time'],float(recInfo['high']),float(recInfo['low'])])
            markEnd5min = datetime.datetime.now()
            Trace.output('info', "Period %s time out at %s and update strategy cost: %s\n"\
                         %(periodName, markStart, str(markEnd5min-markStart)))
            return

        #其他周期定时器
        markQuote = datetime.datetime.now()
        Trace.output('info', "period %s update quote cost: %s"%(periodName,str(markQuote-markStart)))

        #指标计算和记录
        self.indicator.process_indicator(periodName,self.dbQuotationHdl.query_quote(periodName))
        markIndicator = datetime.datetime.now()
        Trace.output('info', "period %s process indicator cost: %s"%(periodName,str(markIndicator-markQuote)))

        #策略算法计算
        self.strategy.check_strategy(periodName,self.dbQuotationHdl.query_quote(periodName))
        markStrategy = datetime.datetime.now()
        Trace.output('info', "period %s check strategy cost: %s\n"%(periodName,str(markStrategy-markIndicator)))

    def statistics_settlement(self):
        """内部接口API: 盈亏统计工作。由汇总各周期盈亏数据库生成表格文件。"""
        for tmName in Constant.QUOTATION_DB_PREFIX[1:]:
            quotefile = Configuration.get_period_working_folder(tmName)+tmName+'-quote.db'
            serfile = Configuration.get_period_working_folder(tmName)+tmName+'-ser.db'
            Primitive.translate_db_into_csv(quotefile) #转csv文件存档
            Primitive.translate_db_into_csv(serfile)


