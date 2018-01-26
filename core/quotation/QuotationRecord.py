#coding=utf-8

from copy import deepcopy
from resource import Constant

class QuotationRecord():
    """ 行情记录类 """
    def __init__(self, flagList):
        self.updatePeriodFlag = flagList
        # QDB中各周期记录字典
        self.recordPeriodDict = {}
        atomicDictItem = dict(zip(Constant.QUOTATION_STRUCTURE,[0,0,0,0,0]))
        # 生成各周期记录字典
        for tagPeriod in Constant.QUOTATION_DB_PREFIX:
            itemPeriod = {tagPeriod: deepcopy(atomicDictItem)}
            self.recordPeriodDict.update(itemPeriod)

    def get_record_dict(self):
        """ 外部接口API: 获取缓冲字典对象 """
        return self.recordPeriodDict

    def update_dict_record(self,infoList):
        """ 外部接口API: 心跳定时器回调函数。更新缓冲记录。
            入参infoList的数据接口：当前价格，当前时间
        """
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
            else:
                dictItem[Constant.QUOTATION_STRUCTURE[4]] = infoList[0]

            #最新价和最高/最低价格进行比较。bug fix only for FX678URL source. 2017-10-25
            if(dictItem[Constant.QUOTATION_STRUCTURE[2]] < infoList[0]):
                dictItem[Constant.QUOTATION_STRUCTURE[2]] = infoList[0]
            elif(dictItem[Constant.QUOTATION_STRUCTURE[3]] > infoList[0]):
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
