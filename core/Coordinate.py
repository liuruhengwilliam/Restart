#coding=utf-8

import os
import datetime

from resource import Configuration
from resource import Constant
from resource import ExceptDeal
from resource import Primitive
from scrape import DataScrape
from indicator.Indicator import Indicator
from quotation import QuotationKit
from quotation.QuotationDB import *
from quotation.QuotationRecord import *
from strategy.Strategy import *
from stratearnrate import StratEarnRate

class Coordinate():
    """
        协作类:衔接“数据抓取”、“行情数据库”、“策略算法”模块，协同工作。
    """
    def __init__(self):
        self.week = (datetime.datetime.now()).strftime('%U')#本周周数记录
        self.workPath = Configuration.get_working_directory() #获取当前周工作路径

        # Quotation record Handle
        self.recordHdl = QuotationRecord(Constant.UPDATE_PERIOD_FLAG)
        self.recordDict = self.recordHdl.get_record_dict()
        # Quotation DB Handle
        self.dbQuotationHdl = QuotationDB(Constant.UPDATE_PERIOD_FLAG,self.recordDict)

        # 指标类初始化
        self.indicator = Indicator()

        # 策略类初始化
        self.strategy = Strategy()

    def init_module(self):
        """ 外部接口API:行情数据库准备 """
        # 创建记录字典
        self.recordHdl.create_record_dict()
        # 创建行情数据库文件
        self.dbQuotationHdl.create_period_db()
        # 创建盈亏数据库文件
        StratEarnRate.create_stratearnrate_db()

    # 以下是定时器回调函数:
    def work_heartbeat(self):
        """ 快速定时器(心跳定时器)回调函数 : 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数 """
        # 全球市场结算期间不更新缓冲记录
        if Constant.is_closing_market():
            self.work_period_details('1day')#此时处理‘1day’周期的相关内容
            return
        if Constant.exit_on_weekend(self.week):#此时处理所有周期的相关内容
            for periodName in Constant.QUOTATION_DB_PREFIX[1:]:
                self.work_period_details(periodName)
            os._exit(0) #退出Python程序

        # 数据抓取并筛选
        infoList = DataScrape.query_info()
        if len(infoList) != 0:
            self.recordHdl.update_dict_record(infoList)

    def work_operation(self):
        """ 外部接口API: 慢速定时器组回调函数--更新行情数据库和策略算法计算 """
        # 定时器名称即是周期名称(defined in Constant.py)
        tmName = threading.currentThread().getName()
        self.work_period_details(tmName)

        #盈亏数据库的操作......

    def work_period_details(self,periodName):
        """ 内部接口API: 某周期的处理细节。
            1.是否结算期及相关处理（转存csv文件和复位相关缓存）；2.更新行情数据库；
            3.行情数据转dateframe格式文件；4.绘制蜡烛图（若需要）；5.调用策略模块进行计算（若需要）
        """
        quotefilename = Configuration.get_period_working_folder(periodName)+periodName+'-quote.db'
        serfilename = Configuration.get_period_working_folder(periodName)+periodName+'-ser.db'

        self.dbQuotationHdl.update_period_db(periodName) #更新行情数据库
        #结算期间由更新标志控制不会多次更新
        if Constant.is_closing_market() or Constant.exit_on_weekend(self.week):
            Primitive.translate_db_into_csv(quotefilename) #转csv文件存档
            Primitive.translate_db_into_csv(serfilename)
            self.recordHdl.reset_dict_record(periodName) #对应周期的行情记录缓存及标志复位
            return

        dataWithId = Primitive.translate_db_to_df(quotefilename)
        if dataWithId is None:
            raise ValueError
            return

        #指标计算和记录
        self.indicator.process_indicator(periodName,dataWithId)
        #策略算法计算

        #策略盈亏率数据库操作。先进行统计更新策略盈亏率数据，然后再分析及插入新条目。
        if periodName == '5min':
            recInfo = self.recordHdl.get_record_dict()['5min']
            self.strategy.update_strategy([recInfo['time'],recInfo['high'],recInfo['low'],recInfo['close']])
        else:
            self.strategy.check_strategy(periodName,dataWithId)

    #盈亏统计工作。由汇总各周期盈亏数据库生成表格文件。
