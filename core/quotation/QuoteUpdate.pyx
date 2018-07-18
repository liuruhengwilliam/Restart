#coding=utf-8

import re
import pandas as pd
from pandas import DataFrame
from resource import Constant
from resource import Trace

def update_quote(record,data,tmCntModList):
    """ 外部接口API: 周期行情数据缓存更新处理函数。基准更新定时器的回调函数。
        target: 对象标的字符串；
        record: Constant类中定义QUOTATION_STRUCTURE = ('time','open','high','low','close')；
        data: DataFrame结构的行情数据；
        tmCntModList: 基础更新定时器的计数值对各周期取余的列表结构；
    """
    # 不更新冗余项。此判断条件的前提是每交易日程序运行延迟不能超过5min，即每次操作的平均时间五秒以内。
    if data.ix[Constant.QUOTATION_DB_PERIOD.index(Constant.UPDATE_BASE_PERIOD),'time'] == record['time']:
        Trace.output('info','Get Cloned info at %s for update base Period'%(record['time']))
        return data

    dataPeriod = data.iloc[:len(Constant.QUOTATION_DB_PERIOD)]
    dataPeriod['mod'] = tmCntModList#增加取余列

    # 到期的周期行处理
    for item in dataPeriod[dataPeriod['mod']==0].itertuples():
        if item[1] == ' ':#程序启动后首次到期'time'项为空，要更新
            data.ix[item[0],1:] = [record[key] for key in Constant.QUOTATION_STRUCTURE]
        else:# 更新条目的截止时间/close价格
            data.ix[item[0],'time'] = record['time']
            data.ix[item[0],'close'] = record['close']
        # 将待存档的条目附着在本DataFrame结构后面。
        data = data.append(data.ix[item[0]],ignore_index=True)
        Trace.output('info','Time out '+' '.join(list(data.iloc[-1].astype(str))))
        # 该Period的下个周期内的首次更新open/high/low。
        data.ix[item[0],2:5] = [record[key] for key in Constant.QUOTATION_STRUCTURE[1:4]]

    # 非到期的周期行处理
    for item in dataPeriod[dataPeriod['mod'] != 0].itertuples():
        if data.ix[item[0],'open'] == 0.0:
            data.ix[item[0],'open'] = record['open']
        if data.ix[item[0],'high'] < record['high']:
            data.ix[item[0],'high'] = record['high']
        if data.ix[item[0],'low'] > record['low'] or data.ix[item[0],'low'] == 0.0:
            data.ix[item[0],'low'] = record['low']

    #print data#调试点
    return data