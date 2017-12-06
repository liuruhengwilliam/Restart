#coding=utf-8

import os
import csv
import sqlite3
import platform
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import matplotlib.ticker as ticker
from pandas import Series,DataFrame
from matplotlib.finance import candlestick_ohlc
from matplotlib.dates import date2num
from matplotlib.dates import DateFormatter
from matplotlib.dates import MinuteLocator,HourLocator,DayLocator,WeekdayLocator

from resource import Constant
from quotation import QuotationKit

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

def show_candlestick(quotes, path,isDraw):
    """ 内部接口API:
        quotes: 数据序列。参照finance类中candlestick_ohlc()方法的入参说明。
        path: 行情数据库文件路径名（包含蜡烛图的周期名称）。
    """
    # 定义相关周期坐标的锚定对象。为了显示清楚锚定值要大于本周期值。
    folderPath,period,timestamp = save_candlestick_misc(path)

    fiveMinLocator = MinuteLocator(interval=20)
    fifteenMinLocator = MinuteLocator(interval=60)
    thirtyMinLocator = MinuteLocator(interval=120)
    oneHourLocator = HourLocator(interval=4)
    twoHourLocator = HourLocator(interval=8)
    fourHourLocator = HourLocator(interval=16)
    sixHourLocator = HourLocator(interval=24)
    twelveHourLocator = HourLocator(interval=48)

    oneDayLocator = DayLocator(interval=2)
    oneWeekLocator = WeekdayLocator(interval=1)

    # 坐标横轴锚定对象列表
    axLocatorList = [None, fiveMinLocator, fifteenMinLocator, thirtyMinLocator,\
        oneHourLocator,twoHourLocator,fourHourLocator,sixHourLocator,twelveHourLocator,\
        oneDayLocator,oneWeekLocator]

    # 定义相关的格式对象。DateFormatter接收的格式化字符与`strftime`相同（参见DateFormatter类定义）
    fiveMinFormatter = fifteenMinFormatter = thirtyMinFormatter = \
        oneHourFormatter = twoHourFormatter = DateFormatter('%H:%M')
    fourHourFormatter = sixHourFormatter = DateFormatter('%b%d %H:%M')
    twelveHourFormatter = oneDayFormatter = DateFormatter('%b %d')
    oneWeekFormatter = DateFormatter('%Y-%m-%d')

    # 坐标横轴格式对象列表
    axFormatterList = [None,fiveMinFormatter, fifteenMinFormatter, thirtyMinFormatter,\
        oneHourFormatter, twoHourFormatter, fourHourFormatter, sixHourFormatter,\
        twelveHourFormatter, oneDayFormatter, oneWeekFormatter]

    fig, ax = plt.subplots(figsize=(20,5))
    fig.subplots_adjust(bottom=0.2)

    # 获取序号--坐标横轴的锚定对象和格式对象列表下标。
    index = Constant.QUOTATION_DB_PREFIX.index(period)

    ax.xaxis.set_major_locator(axLocatorList[index])
    ax.xaxis.set_major_formatter(axFormatterList[index])

    candlestick_ohlc(ax, quotes,width=0.01,colorup='red',colordown='green')
    ax.grid(True)

    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.title(period)
    plt.savefig('%s%s-%s.png'%(folderPath,period,timestamp),dpi=200)
    if isDraw == True:
        plt.show()

def pack_quotes(data):
    """ 内部接口API：处理quotes数据--
        1.去掉id栏
        2.调用date2num函数转换datetime
        data: 二维数组
        返回值: sequence of (time, open, high, low, close, ...) sequences
    """
    quotes = np.array(data.ix[:,['time','open','high','low','close']])

    for q in quotes:
        q[0] = datetime.datetime.strptime(q[0],"%Y-%m-%d %H:%M:%S")
        q[0] = date2num(q[0])

    return quotes

def show_period_candlestick(path,cnt=-1,isDraw=False):
    """ 外部接口API:
        path:行情数据库文件路径
        period:周期数--定义参见Constant包中QUOTATION_DB_PREFIX元组说明。
        cnt:蜡烛图中展示的K线数目。默认展示行情数据库文件中所有记录。
        isDraw:是否展示图画的标志。对于后台运行模式默认不展示。
    """
    dataWithId = QuotationKit.translate_db_to_df(path, cnt)
    if dataWithId is None:
        raise ValueError
        return

    dataPicked = pack_quotes(dataWithId)
    show_candlestick(dataPicked,path,isDraw)

def show_period_candlestick_withCSV(path,cnt=-1,isDraw=False):
    """ 外部接口API:通过CSV文件进行绘制。
        参数说明类同于show_period_candlestick()方法。
    """
    data = []
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            t = row['time'].replace('/','-')#csv文件中时间存储方式需要加以处理
            data.append([t,float(row['open']),float(row['high']),float(row['low']),float(row['close'])])

    title = map(lambda x:x , Constant.QUOTATION_STRUCTURE)
    dataframe = DataFrame(data,columns=title)

    # 组装数据再进行加工
    dataPicked = pack_quotes(dataframe)
    show_candlestick(dataPicked,path,isDraw)