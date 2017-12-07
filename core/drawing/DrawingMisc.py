#coding=utf-8

import os
import platform
import datetime
import numpy as np
from matplotlib.dates import date2num
from resource import Constant
from quotation import QuotationKit
from resource import Trace

def save_candlestick_misc(path):
    """ 内部接口API: 保存蜡烛图文件夹路径和文件名timestamp
        path：数据库文件全路径（蜡烛图文件保存路径同目录）
        返回值：[文件夹路径,周期数,文件名timestamp]
    """
    folder = path.split('.')[0]
    if not os.path.exists(folder):
        os.makedirs(folder)

    if (platform.system() == "Windows"):
        period = folder.split('\\')[-1]
        folder += '\\'
    else:
        period = folder.split('/')[-1]
        folder += '/'

    dt = datetime.datetime.now()
    timestamp = dt.strftime('%b%d_%H_%M')
    return [folder,period,timestamp]

def supplement_quotes(path,dataWithID,supplementCnt):
    """ 内部接口API：补齐K线数目。不考虑*.csv格式文件转换（可手动编辑）。
        path：数据库文件全路径（蜡烛图文件保存路径同目录）
        dataWithID: dataframe结构的数据
        supplementCnt: 需要增补K线的数目
        返回值: 组装之后的sequence of (time, open, high, low, close, ...) sequences
    """
    quotes = np.array(dataWithID.ix[:,['time','open','high','low','close']])
    if (platform.system() == "Windows"):
        segment = path.split('\\')
    else:
        segment = path.split('/')

    if len(segment) < 2:# 数据库文件路径异常
        return quotes

    period = segment[-1]
    weekGap = 1 # 从前一周开始搜索
    while supplementCnt > 0:
        someday = datetime.date.today() - datetime.timedelta(weeks=weekGap)
        year,week = someday.strftime('%Y'),someday.strftime('%U')
        if (platform.system() == "Windows"):
            preDBfile = '\\'.join(segment[:-3]+['%s-%s'%(year,week),'%s'%period])
        else:
            preDBfile = '/'.join(segment[:-3]+['%s-%s'%(year,week),'%s'%period])

        if not os.path.exists(preDBfile): #若回溯文件完毕，则退出循环。
            break

        dataSupplementWithID = QuotationKit.translate_db_to_df(preDBfile, -1)
        dataSupplementCnt = dataSupplementWithID.iloc[-1:]['id']
        if int(dataSupplementCnt) >= supplementCnt: #已经能够补全，取后面的(supplementCnt)个数据
            dataSupplement = np.array(dataSupplementWithID.ix[int(dataSupplementCnt)-supplementCnt:,\
                                ['time','open','high','low','close']])
        else: #还未补全数据继续循环
            dataSupplement = np.array(dataSupplementWithID.ix[:,['time','open','high','low','close']])

        weekGap+=1 #时间回溯
        supplementCnt-=int(dataSupplementCnt) #待补全的数据调整。若为负，则跳出循环。
        quotes = np.vstack((dataSupplement,quotes)) #按照时间顺序收集合并数据

    #Trace.output('info',quotes)
    return quotes

def pack_quotes(path,dataWithID):
    """ 内部接口API：处理quotes数据--
        1.去掉id栏
        2.调用date2num函数转换datetime
        path：数据库文件全路径（蜡烛图文件保存路径同目录）
        dataWithID: dataframe结构的数据
        返回值: sequence of (time, open, high, low, close, ...) sequences
    """
    dataCnt = dataWithID.iloc[-1:]['id']
    if int(dataCnt) >= Constant.CANDLESTICK_DEFAULT_CNT:
        # 取从第（dataCnt-Constant.CANDLESTICK_DEFAULT_CNT个）到最后一个（第dataCnt）的数据
        # （共Constant.CANDLESTICK_DEFAULT_CNT个）
        quotes = np.array(dataWithID.ix[(int(dataCnt)-Constant.CANDLESTICK_DEFAULT_CNT):,\
                          ['time','open','high','low','close']])
    else:# 要补齐蜡烛图中K线数目
        quotes = supplement_quotes(path,dataWithID,int(Constant.CANDLESTICK_DEFAULT_CNT-int(dataCnt)))

    for q in quotes:
        q[0] = datetime.datetime.strptime(q[0],"%Y-%m-%d %H:%M:%S")
        q[0] = date2num(q[0])

    return quotes
