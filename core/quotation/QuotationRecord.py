#coding=utf-8

from copy import deepcopy
from resource import Constant

class QuotationRecord():
    """ 行情记录类 """
    def __init__(self, flagList, updateLock):
        self.updatePeriodFlag = flagList
        self.updateLock = updateLock

        # QDB中各周期记录字典
        self.recordPeriodDict = {}

    # 用列表还是用字典？ 字典可读性优于列表，后期维护性较高。-- 字典'键值对'本身就是一种注释。
    def create_record_dict(self):
        """ 外部接口API: 创建记录字典: '缓冲记录字典' 和 '各周期记录字典' """
        atomicDictItem = dict(zip(Constant.QUOTATION_STRUCTURE,[0,0,0,0,'']))

        # 生成各周期记录字典
        for tagPeriod in list(Constant.QUOTATION_DB_PREFIX):
            itemPeriod = {tagPeriod: deepcopy(atomicDictItem)}
            self.recordPeriodDict.update(itemPeriod)

    def get_record_dict(self):
        """ 外部接口API: 获取记录字典 """
        return self.recordPeriodDict

    def update_dict_record(self,infoList):
        """ 外部接口API: 心跳定时器回调函数。更新缓冲记录。
            入参infoList的数据接口：当前价格，当前时间
        """

        #用最快定时器（心跳定时器）来更新其他周期行情数据记录
        for i in range(len(Constant.QUOTATION_DB_PERIOD)):
            dictItem = self.recordPeriodDict[Constant.QUOTATION_DB_PREFIX[i]]
            # 设置记录时间
            dictItem[Constant.QUOTATION_STRUCTURE[4]] = infoList[1]

            self.updateLock[i].acquire()
            #每次行情数据库更新后各周期定时器首次到期时，开盘价/最高/最低都等于实时价格，且开盘价后续不更新。
            #对于最快定时器（暂定6秒），忽略该设置。
            if self.updatePeriodFlag[i] == True:
                dictItem[Constant.QUOTATION_STRUCTURE[0]] = \
                dictItem[Constant.QUOTATION_STRUCTURE[1]] = \
                dictItem[Constant.QUOTATION_STRUCTURE[2]] = \
                dictItem[Constant.QUOTATION_STRUCTURE[3]] = infoList[0]
                self.updatePeriodFlag[i] = False
                self.updateLock[i].release()
                continue
            else:
                dictItem[Constant.QUOTATION_STRUCTURE[3]] = infoList[0]
            self.updateLock[i].release()

            #最新价和最高/最低价格进行比较。bug fix only for FX678URL source. 2017-10-25
            if(dictItem[Constant.QUOTATION_STRUCTURE[1]] < infoList[0]):
                dictItem[Constant.QUOTATION_STRUCTURE[1]] = infoList[0]
            elif(dictItem[Constant.QUOTATION_STRUCTURE[2]] > infoList[0]):
                dictItem[Constant.QUOTATION_STRUCTURE[2]] = infoList[0]
