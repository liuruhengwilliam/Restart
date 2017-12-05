#coding=utf-8

import sqlite3
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

def show_candlestick(quotes, period):
    """ 内部接口API:
        quotes: 数据序列。参照finance类中candlestick_ohlc()方法的入参说明。
        period: 蜡烛图的周期名称。
    """
    # 定义相关周期坐标的锚定对象
    fiveMinLocator = MinuteLocator(interval=5)
    fifteenMinLocator = MinuteLocator(interval=15)
    thirtyMinLocator = MinuteLocator(interval=30)

    oneHourLocator = HourLocator(interval=1)
    twoHourLocator = HourLocator(interval=2)
    fourHourLocator = HourLocator(interval=4)
    sixHourLocator = HourLocator(interval=6)
    twelveHourLocator = HourLocator(interval=12)

    oneDayLocator = DayLocator(interval=1)
    oneWeekLocator = WeekdayLocator(interval=1)

    # 坐标横轴锚定对象列表
    axLocatorList = [None, fiveMinLocator, fifteenMinLocator, thirtyMinLocator,\
        oneHourLocator,twoHourLocator,fourHourLocator,sixHourLocator,twelveHourLocator,\
        oneDayLocator,oneWeekLocator]

    # 定义相关的格式对象。DateFormatter接收的格式化字符与`strftime`相同（参见DateFormatter类定义）
    fiveMinFormatter = fifteenMinFormatter = thirtyMinFormatter = DateFormatter('%M')
    oneHourFormatter = twoHourFormatter = fourHourFormatter = \
        sixHourFormatter = twelveHourFormatter = DateFormatter('%H')
    oneDayFormatter = DateFormatter('%d')
    oneWeekFormatter = DateFormatter('%b %d')

    # 坐标横轴格式对象列表
    axFormatterList = [None,fiveMinFormatter, fifteenMinFormatter, thirtyMinFormatter,\
        oneHourFormatter, twoHourFormatter, fourHourFormatter, sixHourFormatter,\
        twelveHourFormatter, oneDayFormatter, oneWeekFormatter]

    fig, ax = plt.subplots(figsize=(10,5))
    fig.subplots_adjust(bottom=0.2)

    # 获取序号--坐标横轴的锚定对象和格式对象列表下标。
    index = Constant.QUOTATION_DB_PREFIX.index(period)

    ax.xaxis.set_major_locator(axLocatorList[index])
    ax.xaxis.set_major_formatter(axFormatterList[index])

    candlestick_ohlc(ax, quotes,width=0.01,colorup='red',colordown='green')
    ax.grid(True)
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

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
        print q,type(q[0])
        q[0] = datetime.datetime.strptime(q[0],"%Y-%m-%d %H:%M:%S")
        q[0] = date2num(q[0])

    return quotes

def show_period_candlestick(path,period,cnt=-1):
    """ 外部接口API:
        path:行情数据库文件路径
        period:周期数--定义参见Constant包中QUOTATION_DB_PREFIX元组说明。
        cnt:蜡烛图中展示的K线数目。默认展示行情数据库文件中所有记录。
    """
    dataWithId = QuotationKit.translate_db_to_df(path, cnt)
    if dataWithId is None:
        raise ValueError
        return

    dataPicked = pack_quotes(dataWithId)
    show_candlestick(dataPicked,period)
