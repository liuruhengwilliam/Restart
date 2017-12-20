#coding=utf-8

import os
import datetime

from resource import Configuration
from resource import Constant
from resource import ExceptDeal
from scrape import DataScrape
from drawing import DrawingKit
from quotation import QuotationKit
from earnrate.EarnrateDB import *
from quotation.QuotationDB import *
from quotation.QuotationRecord import *
from strategy import Strategy

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
        # Earnrate DB Handle
        self.dbEarnrateHdl = EarnrateDB(self.workPath)

    def init_module(self):
        """ 外部接口API:行情数据库准备 """
        # 创建记录字典
        self.recordHdl.create_record_dict()
        # 创建行情数据库文件
        self.dbQuotationHdl.create_period_db()
        # 创建盈亏数据库文件
        self.dbEarnrateHdl.create_earnrate_db()

    # 以下是定时器回调函数:
    def work_heartbeat(self):
        """ 快速定时器(心跳定时器)回调函数 : 数据抓取模块和行情数据库线程(缓冲字典)之间协同工作函数 """
        # 全球市场结算期间不更新缓冲记录
        if Constant.is_closing_market():
            self.deal_day_closing()
            return
        if Constant.exit_on_weekend(self.week):
            self.deal_week_closing()
            return

        # 数据抓取并筛选
        infoList = DataScrape.query_info()
        if len(infoList) != 0:
            self.recordHdl.update_dict_record(infoList)

    def work_operation(self):
        """ 外部接口API: 慢速定时器组回调函数--更新行情数据库和策略算法计算 """
        # 通过定时器名称获取当前到期的周期序号(defined in Constant.py)
        tmName = threading.currentThread().getName()
        indx = Constant.QUOTATION_DB_PREFIX.index(tmName)
        #拼装文件路径和文件名
        file = Configuration.get_period_working_folder(tmName)+tmName+'.db'

        # 全球市场结算时间不更新数据库
        if Constant.is_closing_market():# 当日结算
            QuotationKit.translate_db_into_csv(file) #转csv文件存档
            return
        if Constant.exit_on_weekend(self.week):
            return

        self.dbQuotationHdl.update_period_db(tmName) #更新行情数据库

        dataWithId = QuotationKit.translate_db_to_df(file)
        if dataWithId is None:
            raise ValueError
            return

        DrawingKit.show_period_candlestick(tmName,dataWithId) #转蜡烛图文件存档
        # 各周期定时器到期之后，可根据需求调用策略算法模块的接口API对本周期数据进行计算。
        Strategy.check_strategy(tmName,dataWithId)

    def deal_day_closing(self):
        """ 内部接口API: 每日闭市时相关处理。挂载在心跳定时器回调函数中 """
        index1day = Constant.QUOTATION_DB_PREFIX.index('1day')
        file1day = Configuration.get_period_working_folder('1day')+'1day.db'

        self.dbQuotationHdl.update_period_db('1day')
        #转csv和蜡烛图文件存档的工作在周结算期统一完成。
        dataWithId = QuotationKit.translate_db_to_df(file1day)
        if dataWithId is None:
            raise ValueError
            return

        # 策略算法计算。
        Strategy.check_strategy('1day',dataWithId)

    def deal_week_closing(self):
        """ 内部接口API: 每周闭市时相关处理。挂载在心跳定时器回调函数中 """
        #对于所有周期（心跳周期除外）进行更新
        for tmName in Constant.QUOTATION_DB_PREFIX[1:]:
            self.dbQuotationHdl.update_period_db(tmName) #更新行情数据库

            filePath = Configuration.get_period_working_folder(tmName)+tmName+'.db'
            #转csv文件存档
            QuotationKit.translate_db_into_csv(filePath)

            dataWithId = QuotationKit.translate_db_to_df(filePath)
            if dataWithId is None:
                raise ValueError
                return
            #绘制蜡烛图文件存档
            indexPeriod = Constant.QUOTATION_DB_PREFIX.index(tmName)
            DrawingKit.show_period_candlestick(indexPeriod, filePath, dataWithId)

            #策略计算
            #Strategy.check_strategy(tmName,dataWithId)

        os._exit() #退出Python程序