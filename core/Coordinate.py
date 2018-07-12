#coding=utf-8

import re
import os
import datetime
from resource import Trace
from resource import Configuration
from resource import Constant
from scrape.DataScrape import query_info_futures
from scrape.DataScrape import query_info_stock
from indicator.Indicator import Indicator
from quotation.Quotation import *
from quotation.QuotationRecord import *
from quotation.QuoteUpdate import update_quote
from strategy.Strategy import Strategy
from strategy.StrategyUpdate import update_strategy
from strategy.StrategyCheck import check_strategy

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
        self.strategy = Strategy(self.recordHdl.get_target_list())
        Trace.output('info', " ==== ==== Server Complete Initiation and Run Routine ==== ==== \n")

    # 以下是定时器回调函数:
    def work_heartbeat(self):
        """ 外部函数API：抓取某股票代码的实时行情数据处理函数 """
        markStart = datetime.datetime.now()
        for target in self.recordHdl.get_target_list():
            if target == '':#分解出的异常字符
                continue
            if Constant.is_closed(target):#当前是否为闭市时间
                return

            # 通过正则表达式来区分标的类型：股票（数字） or 大宗商品（英文字母）
            # re.match(r'[a-zA-Z](.*)',target)#re.match在字符串开始处匹配模式
            if re.search(r'[^a-zA-Z]',target) is None:#大宗商品类型全是英文字母
                infoList = query_info_futures()
                if len(infoList) != 2:
                    Trace.output('warn',"Faile to query:%s"%target)
                    continue
                # 更新record
                self.recordHdl.update_futures_record([target]+infoList)
            elif re.search(r'[^0-9](.*)',target) is None:#股票类型全是数字
                quoteList = query_info_stock(target)
                if quoteList is None or len(quoteList) != len(Constant.QUOTATION_STRUCTURE):
                    Trace.output('warn',"Faile to query:%s"%target)
                    continue
                # 更新record
                self.recordHdl.update_stock_record([target]+quoteList)
            else:#错误类型
                Trace.output('warn',"ERROR target:%s"%target)
                continue

        markQuery = datetime.datetime.now()
        Trace.output('info', "It cost %s to query target(%s) at %s."%\
                     (str(markQuery-markStart),' '.join(self.recordHdl.get_target_list()),markStart))

    def work_operation(self):
        """ 外部函数API：股票代码的周期行情数据缓存处理函数
            挂载在基准定时器。根据倍数关系，驱动更新其他大周期行情数据缓存。
        """
        markStart = datetime.datetime.now()
        baseTmCnt = self.quoteHdl.get_baseTM_cnt()
        for target in self.recordHdl.get_target_list():
            if target == '':#分解出的异常字符
                continue
            if Constant.be_exited(target):
                os._exit(0)
            if Constant.is_closed(target):#当前是否为闭市时间
                return

            markStartTarget = datetime.datetime.now()

            # 更新各周期行情数据缓存
            quoteDF = self.quoteHdl.get_quote(target)
            record = self.recordHdl.get_record_dict(target)
            if record is None:
                continue
            quoteDF = update_quote(record,quoteDF,baseTmCnt)
            # 更新之后要回写行情数据
            self.quoteHdl.set_quote(target,quoteDF)
            self.recordHdl.reset_target_record(target)

            markQuoteUpd = datetime.datetime.now()
            Trace.output('debug',"For %s,update quote cost:%s"%(target,str(markQuoteUpd-markStartTarget)))

            if len(quoteDF) <= len(Constant.QUOTATION_DB_PERIOD):#无附着条目直接返回
                continue

            # 在基础更新定时器到期时更新策略记录条目
            baseTmIndx = Constant.QUOTATION_DB_PERIOD.index(Constant.UPDATE_BASE_PERIOD)
            infoList = [quoteDF.time[baseTmIndx],quoteDF.high[baseTmIndx],quoteDF.low[baseTmIndx]]
            dfStrategy = update_strategy(self.strategy.get_strategy(target),infoList)

            markStrgUpd = datetime.datetime.now()
            Trace.output('debug',"For %s,update strategy cost:%s"%(target,str(markStrgUpd-markQuoteUpd)))

            # 策略匹配并生成条目(若有)
            dfRet = check_strategy(baseTmCnt,quoteDF)
            # 策略新条目要回写
            self.strategy.set_strategy(target,dfRet)

            markStrgChk = datetime.datetime.now()
            Trace.output('debug',"For %s,check strategy cost:%s"%(target,str(markStrgChk-markStrgUpd)))

            if re.search(r'[^a-zA-Z]',target) is None:#股票转存由专门的线程负责，不再这里处理。
                # 每小时存储一次
                if baseTmCnt%(Constant.QUOTATION_DB_PERIOD[4]/Constant.UPDATE_BASE_PERIOD)==0:
                    self.storage_data(target)#转存数据到csv文件
        # 基准定时器计数自增
        self.quoteHdl.increase_baseTM_cnt()

        markEnd = datetime.datetime.now()
        Trace.output('info', "It totally cost %s to operate target(%s) from %s"%\
                     (str(markEnd-markStart),' '.join(self.recordHdl.get_target_list()),markStart))

    def work_storage(self):
        """ 外部函数API：数据存档线程的处理函数。30min
        """
        markStart = datetime.datetime.now()
        for target in self.recordHdl.get_target_list():
            if re.search(r'[^0-9](.*)',target) is None:#股票类型全是数字
                # 股票类型数据较多，需要加以控制。拟定每半小时存储一次。
                baseTmCnt = self.quoteHdl.get_baseTM_cnt()
                if baseTmCnt%(Constant.QUOTATION_DB_PERIOD[3]/Constant.UPDATE_BASE_PERIOD)!=0 \
                        and Constant.is_closed(target)==False:
                    #在非结算期中未到期不记录
                    return

            self.storage_data(target)
        markEnd = datetime.datetime.now()
        Trace.output('info', "It cost %s to store target(%s) at %s"%\
                     (str(markEnd-markStart),' '.join(self.recordHdl.get_target_list()),markStart))

    def storage_data(self,target):
        """ 内部函数API：转存相关数据
            target: 标的字符串
        """
        #更新行情数据到csv文件中
        quoteRecord = self.quoteHdl.get_quote(target).iloc[len(Constant.QUOTATION_DB_PERIOD):]
        quoteRecord.to_csv(Configuration.get_working_directory()+target+'-quote.csv',\
                            columns=['period',]+list(Constant.QUOTATION_STRUCTURE),index=False)
        # 更新策略匹配数据到csv文件
        self.strategy.get_strategy(target).to_csv(Configuration.get_working_directory()+target\
                            +'-ser.csv',columns=Constant.SER_DF_STRUCTURE, index=False)
