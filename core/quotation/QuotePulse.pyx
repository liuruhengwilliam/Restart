#coding=utf-8

import pandas as pd
from pandas import DataFrame
from resource import Constant
from resource import Trace

def update_quote(record,data,modList):
    """ 外部接口API: 周期行情数据缓存更新处理函数。基准更新定时器的回调函数。
        record: Constant类中定义QUOTATION_STRUCTURE = ('time','open','high','low','close')；
        data: DataFrame结构的行情数据；
        modList: 计数值对各周期(Constant.QUOTATION_DB_PREFIX)取余列表；
    """

    # 更新基准定时器及高阶定时器的记录缓存
    for index,modVal in enumerate(modList):
        # 无关周期不处理。
        if modVal == -1:
            continue

        # 高阶定时器的一个周期完结，先存档旧条目，后更新条目
        if modVal == 0:
            # 不更新冗余项。驱动定时周期会漂移，通过闭市时间不易保证
            if data.ix[index,'time'] == record['time']:
                Trace.output('warn','get Cloned info at %s'%(record['time']))
                continue
            if data.ix[index,'time'] == ' ':#程序启动后首次到期更新
                data.ix[index,1:] = [record[key] for key in Constant.QUOTATION_STRUCTURE]
            else:# 更新条目的截止时间/close价格
                data.ix[index,'time'] = record['time']
                data.ix[index,'close'] = record['close']
            # 将待存档的条目附着在本DataFrame结构后面。
            data = data.append(data.ix[index],ignore_index=True)
            Trace.output('info',':Time out '+' '.join(list(data.iloc[-1].astype(str))))
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
