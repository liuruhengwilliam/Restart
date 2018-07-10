#coding=utf-8

import re
import pandas as pd
from pandas import DataFrame
from resource import Constant
from resource import Trace

def mod_period_list(target,baseTmCnt):
    """ 外部接口API: 获取当前计数对各周期的去模列表。
        返回值： 取模之后的列表结构。
        target: 对象标的字符串
        baseTmCnt: 基础更新定时器的计数值
    """
    modList = []
    if re.search(r'[^a-zA-Z]',target) is None:
        modList.append(-1)
        for period in Constant.QUOTATION_DB_PERIOD[1:-1]:#from 5min to 1day
            modList.append(baseTmCnt%(period/Constant.UPDATE_BASE_PERIOD))
        modList.append(-1)
    elif re.search(r'[^0-9](.*)',target) is None:#from 5min to 4hour
        modList.append(-1)
        for period in Constant.QUOTATION_DB_PERIOD[1:-5]:#from 5min to 4hour
            modList.append(baseTmCnt%(period/Constant.UPDATE_BASE_PERIOD))
        modList = modList + [-1]*5
    return modList

def update_quote(target,record,data,baseTmCnt):
    """ 外部接口API: 周期行情数据缓存更新处理函数。基准更新定时器的回调函数。
        target: 对象标的字符串；
        record: Constant类中定义QUOTATION_STRUCTURE = ('time','open','high','low','close')；
        data: DataFrame结构的行情数据；
        baseTmCnt: 基础更新定时器的计数值；
    """

    # 更新基准定时器及高阶定时器的记录缓存
    for index,modVal in enumerate(mod_period_list(target,baseTmCnt)):
        # 无关周期不处理。
        if modVal == -1:
            continue

        # 高阶定时器的一个周期完结，先存档旧条目，后更新条目
        if modVal == 0:
            # 不更新冗余项。驱动定时周期会漂移，通过闭市时间不易保证
            if data.ix[index,'time'] == record['time']:
                Trace.output('warn',target+' get Cloned info at %s for Period %s'%(record['time'],index))
                continue
            if data.ix[index,'time'] == ' ':#程序启动后首次到期更新
                data.ix[index,1:] = [record[key] for key in Constant.QUOTATION_STRUCTURE]
            else:# 更新条目的截止时间/close价格
                data.ix[index,'time'] = record['time']
                data.ix[index,'close'] = record['close']
            # 将待存档的条目附着在本DataFrame结构后面。
            data = data.append(data.ix[index],ignore_index=True)
            Trace.output('info',target+':Time out '+' '.join(list(data.iloc[-1].astype(str))))
            # 该Period的下个周期内的首次更新open/high/low。
            data.ix[index,2:5] = [record[key] for key in Constant.QUOTATION_STRUCTURE[1:4]]
        else:
            if data.ix[index,'open'] == 0.0:
                data.ix[index,'open'] = record['open']
            if data.ix[index,'high'] < record['high']:
                data.ix[index,'high'] = record['high']
            if data.ix[index,'low'] > record['low'] or data.ix[index,'low'] == 0.0:
                data.ix[index,'low'] = record['low']

    #print data#调试点
    return data
