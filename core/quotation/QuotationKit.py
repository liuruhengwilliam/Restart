#coding=utf-8

import os
import numpy as np
import pandas as pd
from pandas import DataFrame
from resource import Configuration
from resource import Constant
from resource import Primitive
from resource import Trace

def supplement_quotes(periodName,dataWithID,supplementCnt):
    """ 外部接口API：补齐某个数目的行情序列。不考虑*.csv格式文件转换（可手动编辑）。
        periodName：周期名称字符串
        dataWithID: 当前周期行情数据库文件的dataframe结构数据
        supplementCnt: 需要增补的数目
        返回值: 增补后的dateframe结构行情数据
    """
    quotes = np.array(dataWithID.ix[:])
    weekGap = 1 # 从前一周开始搜索
    while supplementCnt > 0:
        preDBfile = Configuration.get_backweek_period_directory(weekGap, periodName)+periodName+'-quote.db'
        if not os.path.exists(preDBfile): #若回溯文件完毕，则退出循环。
            break

        dataSupplementWithID = Primitive.translate_db_to_df(preDBfile)
        dataSupplementCnt = dataSupplementWithID.iloc[-1:]['id']
        if len(dataSupplementCnt) == 0:
            #对于无记录文件情形，dataSupplementCnt为空Series。int(dataSupplementCnt)会报错。
            supplCnt = 0
        else:
            supplCnt = int(dataSupplementCnt)
        if supplCnt >= supplementCnt: #已经能够补全，取后面的(supplementCnt)个数据
            dataSupplement = np.array(dataSupplementWithID.ix[supplCnt-supplementCnt:])
        else: #还未补全数据继续循环
            dataSupplement = np.array(dataSupplementWithID.ix[:])

        weekGap+=1 #时间回溯
        supplementCnt-=supplCnt #待补全的数据调整。若为负，则跳出循环。
        quotes = np.vstack((dataSupplement,quotes)) #按照时间顺序收集合并数据

    # 抬头信息
    title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)
    dataframe = DataFrame(quotes,columns=title)

    return dataframe
