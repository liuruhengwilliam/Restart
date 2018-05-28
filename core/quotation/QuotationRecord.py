#coding=utf-8

import os
from copy import deepcopy
from resource import Constant
from resource import Configuration

class QuotationRecord():
    """ 行情记录类 """
    def __init__(self):
        """ 行情实时数据处理模块初始化函数 """
        target = Configuration.parse_target_list()
        # QDB中各周期记录字典
        self.recordPeriodDict = {}
        if len(target)==0:#未配置就默认为'Silver'
            self.quoteList = ['Silver']
        else:
            self.quoteList = target

        atomicDictItem = dict(zip(Constant.QUOTATION_STRUCTURE,[' ',0.0,0.0,0.0,0.0]))
        for name in self.quoteList:# 生成期货/大宗商品/股票代码和TOHLC字典项。周期标记因子在定时器中叠加。
            self.recordPeriodDict.update({name:deepcopy(atomicDictItem)})

    def get_record_dict(self,target):
        """ 外部接口API: 获取缓冲字典对象 """
        return self.recordPeriodDict[target]

    def get_target_list(self):
        """ 外部接口API: 获取标的列表 """
        return self.quoteList

    def update_stock_record(self,infoList):
        """ 外部接口API: 心跳定时器回调函数。更新缓冲记录。
            入参infoList的数据接口：[stockID,time,open,high,low,close]
        """
        stock,time,open,high,low,close = infoList
        self.recordPeriodDict[stock]['time']=time
        self.recordPeriodDict[stock]['close']=close
        if self.recordPeriodDict[stock]['open'] == 0.0:
            self.recordPeriodDict[stock]['open']=open
        if self.recordPeriodDict[stock]['high']<high:
            self.recordPeriodDict[stock]['high']=high
        if self.recordPeriodDict[stock]['low']==0.0 or self.recordPeriodDict[stock]['low']>low:
            self.recordPeriodDict[stock]['low']=low

    def update_futures_record(self,infoList):
        """ 外部接口API: 心跳定时器回调函数。更新缓冲记录。
            入参infoList的数据接口：[target,time,price]
        """
        future,price,time = infoList
        self.recordPeriodDict[future]['time']=time
        self.recordPeriodDict[future]['close']=price
        if self.recordPeriodDict[future]['open'] == 0.0:
            self.recordPeriodDict[future]['open']=price
        if self.recordPeriodDict[future]['high'] < price:
            self.recordPeriodDict[future]['high']=price
        if self.recordPeriodDict[future]['low'] == 0.0 or self.recordPeriodDict[future]['low'] > price:
            self.recordPeriodDict[future]['low']=price

    def reset_target_record(self,target):
        self.recordPeriodDict[target]['time']=' '
        self.recordPeriodDict[target]['open'] = 0.0
        self.recordPeriodDict[target]['high'] = 0.0
        self.recordPeriodDict[target]['low'] = 0.0
        self.recordPeriodDict[target]['close'] = 0.0
