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

def process_quotes_drawing_candlestick(index,path,dataWithID):
    """ 外部接口API：处理quotes数据
        1.去掉id栏
        2.调用date2num函数转换datetime
        index:周期序列的下标
        path：数据库文件全路径（包含文件名，蜡烛图文件保存路径同目录）
        dataWithID: dataframe结构的数据
        返回值: sequence of (time, open, high, low, close, ...) sequences
    """
    dataCnt = dataWithID.iloc[-1:]['id']
    gap = int(dataCnt)-Constant.CANDLESTICK_PERIOD_CNT[index]
    if gap >= 0:
        # 取从第（dataCnt-X个）到最后一个（第dataCnt）的数据（共X个）
        quotes = np.array(dataWithID.ix[int(gap):,['time','open','high','low','close']])
    else:# 要补齐蜡烛图中K线数目
        dataSupplementWithID = QuotationKit.supplement_quotes(path,dataWithID,int(abs(gap)))
        quotes = np.array(dataSupplementWithID.ix[:,['time','open','high','low','close']])

    for q in quotes:
        q[0] = datetime.datetime.strptime(q[0],"%Y-%m-%d %H:%M:%S")
        q[0] = date2num(q[0])

    return quotes