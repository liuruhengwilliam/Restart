#coding=utf-8

from copy import deepcopy
from resource import Constant
from resource import Configuration

class QuotationRecord():
    """ 行情记录类 """
    def __init__(self):
        """ 行情实时数据处理模块初始化函数 """
        self.quoteTypeList = Configuration.get_stock_list()
        # QDB中各周期记录字典
        self.recordPeriodDict = {}
        if self.quoteTypeList is None:# 单一期货/现货类型
            # 各周期更新标志--计数装置
            self.updatePeriodFlag = [True]*len(Constant.QUOTATION_DB_PREFIX)
            atomicDictItem = dict(zip(Constant.QUOTATION_STRUCTURE,[0,0,0,0,0]))
            # 生成各周期记录字典
            for tagPeriod in Constant.QUOTATION_DB_PREFIX:
                itemPeriod = {tagPeriod: deepcopy(atomicDictItem)}
                self.recordPeriodDict.update(itemPeriod)
        else:# 股票列表类型
            self.updatePeriodFlag = {}
            # 各周期更新标志
            atomUpdateFlag = list(Constant.QUOTATION_DB_PERIOD)
            atomicDictItem = dict(zip(Constant.QUOTATION_STRUCTURE,[' ',0.0,0.0,0.0,0.0]))
            for id in self.quoteTypeList:# 生成股票代码和TOHLC字典项。周期标记因子在Quotation类中叠加。
                self.updatePeriodFlag.update({id:deepcopy(atomUpdateFlag)})
                self.recordPeriodDict.update({id:deepcopy(atomicDictItem)})

    def get_record_dict(self):
        """ 外部接口API: 获取缓冲字典对象 """
        return self.recordPeriodDict

    def get_stock_list(self):
        """ 外部接口API: 获取股票列表 """
        return self.quoteTypeList

    def get_period_flag(self):
        """ 外部接口API: 获取更新标志列表对象 """
        return self.updatePeriodFlag

    def update_stock_record(self,infoList):
        """ 外部接口API: 心跳定时器回调函数。更新缓冲记录。
            入参infoList的数据接口：[stockID,time,open,high,low,close]
        """
        stockID,time,open,high,low,close = infoList
        self.recordPeriodDict[stockID]['time'] = time
        self.recordPeriodDict[stockID]['open'] = open
        self.recordPeriodDict[stockID]['high'] = high
        self.recordPeriodDict[stockID]['low'] = low
        self.recordPeriodDict[stockID]['close'] = close

    def update_dict_record(self,infoList):
        """ 外部接口API: 心跳定时器回调函数。更新缓冲记录。
            入参infoList的数据接口：当前价格，当前时间
        """
        if infoList[1].strftime("%S") == '00':#为减少计时中0秒带来的异常处理，强制秒计数为01
            infoList[1] = infoList[1].replace(second=1)
        #用最快定时器（心跳定时器）来更新其他周期行情数据记录
        for tagPeriod,dictItem in self.recordPeriodDict.items():
            # 设置记录时间
            dictItem[Constant.QUOTATION_STRUCTURE[0]] = infoList[1]

            #每次行情数据库更新后各周期定时器首次到期时，开盘价/最高/最低都等于实时价格，且开盘价后续不更新。
            #对于最快定时器（暂定6秒），忽略该设置。
            if self.updatePeriodFlag[Constant.QUOTATION_DB_PREFIX.index(tagPeriod)] == True:
                dictItem[Constant.QUOTATION_STRUCTURE[1]] = \
                dictItem[Constant.QUOTATION_STRUCTURE[2]] = \
                dictItem[Constant.QUOTATION_STRUCTURE[3]] = \
                dictItem[Constant.QUOTATION_STRUCTURE[4]] = infoList[0]
                self.updatePeriodFlag[Constant.QUOTATION_DB_PREFIX.index(tagPeriod)] = False
                continue

            if dictItem[Constant.QUOTATION_STRUCTURE[1]] == 0.0:#开盘价不可能为零
                dictItem[Constant.QUOTATION_STRUCTURE[1]] = infoList[0]

            dictItem[Constant.QUOTATION_STRUCTURE[4]] = infoList[0]#更新收盘价

            #最新价和最高/最低价格进行比较。bug fix only for FX678URL source. 2017-10-25
            if dictItem[Constant.QUOTATION_STRUCTURE[2]] < infoList[0]:#更新最高价
                dictItem[Constant.QUOTATION_STRUCTURE[2]] = infoList[0]
            elif dictItem[Constant.QUOTATION_STRUCTURE[3]] > infoList[0] \
                    or dictItem[Constant.QUOTATION_STRUCTURE[3]] == 0.0:#最低价不可能为零
                dictItem[Constant.QUOTATION_STRUCTURE[3]] = infoList[0]

    def reset_dict_record(self,periodName):
        """ 外部接口API: 复位某周期行情缓存记录及标志
            periodName: 周期名称的字符串
        """
        dictItem = self.recordPeriodDict[periodName] #对字典项通过键找到对应的值

        dictItem[Constant.QUOTATION_STRUCTURE[0]] =\
        dictItem[Constant.QUOTATION_STRUCTURE[1]] =\
        dictItem[Constant.QUOTATION_STRUCTURE[2]] =\
        dictItem[Constant.QUOTATION_STRUCTURE[3]] =\
        dictItem[Constant.QUOTATION_STRUCTURE[4]] = 0
        #self.updatePeriodFlag[Constant.QUOTATION_DB_PREFIX.index(periodName)] = True
