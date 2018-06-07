#coding=utf-8
import sys
import csv
import sqlite3
import datetime
import traceback
import platform
if (platform.system() == "Linux"):#适配Linux系统下运行环境
    import matplotlib
    matplotlib.use("Pdf")
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
from matplotlib.finance import candlestick_ohlc
from matplotlib.dates import DateFormatter
from matplotlib.dates import MinuteLocator,HourLocator,DayLocator,WeekdayLocator
import DataProcess
from resource import Constant
from resource import Configuration
from quotation import QuotationKit
from indicator import MA
from indicator import BollingerBands

def show_candlestick(target,dfData, ma, BBands, periodName):
    """ 内部接口API:
        dfData: Dataframe数据接口。
        ma： 移动平均线数据列表
        BBands：布林线数据列表（上/中/下轨）
        periodName: 周期名称的字符串。
    """
    fig, ax = plt.subplots(figsize=(20,10))
    fig.subplots_adjust(bottom=0.2)

    # 获取序号--坐标横轴的锚定对象和格式对象列表下标。
    index = Constant.QUOTATION_DB_PREFIX.index(periodName)

    #quotes: 数据序列。参照finance类中candlestick_ohlc()方法的入参说明。
    quotes = np.array(dfData[['dt2num','open','high','low','close']])
    try:
        # 设置坐标横轴的起止位置。参见numpy.ndarray类的处理方法。
        ax.set_xlim([quotes.item(0,0),quotes.item(-1,0)])
        candlestick_ohlc(ax, quotes,width=0.001,colorup='red',colordown='green')

        # 刷新X轴的ticks('dt2num')和labels('time')
        labels = DataProcess.process_xaxis_labels(index, dfData['time'].as_matrix()[::4])
        plt.xticks([tm for tm in dfData['dt2num'].as_matrix()[::4]],labels)

        # 均线
        for index in range(len(Constant.MOVING_AVERAGE_LINE)):
            if len(ma[index]) > 0:
                # 通过ax.get_xticks()可以获取横轴坐标。但此处横轴坐标已经缩减，不可使用。
                tag = Constant.MOVING_AVERAGE_LINE[index]
                ax.plot(dfData['dt2num'].as_matrix()[tag-1:],ma[index],lw=0.8,label="MA%s"%str(tag))

        # 布林线
        upperBB,middleBB,lowerBB = BBands
        ax.plot(dfData['dt2num'].as_matrix()[Constant.BOLLINGER_BANDS-1+2:],upperBB[2:],'y--',label="UBB")
        ax.plot(dfData['dt2num'].as_matrix()[Constant.BOLLINGER_BANDS-1:],middleBB,'y:',label="MBB")
        ax.plot(dfData['dt2num'].as_matrix()[Constant.BOLLINGER_BANDS-1+2:],lowerBB[2:],'y--',label="LBB")

        # 坐标横轴锚定数目太多，为避免报错直接返回。
        if len(ax.get_xticklabels()) >= max(Constant.CANDLESTICK_PERIOD_CNT):
            return
        if (platform.system() == "Windows"):#Linux环境下不进行下列优化
            plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')

        # 设置抬头和Y轴标签
        ax.grid(True)
        ax.legend()
        plt.title(target+'  '+periodName)
        plt.ylabel("Price ($)")
        # 生成图片文件保存
        timestamp = datetime.datetime.now().strftime('%b%d_%H_%M')
        plt.savefig('%s%s-%s-%s.png'%(Configuration.get_working_directory(),target,periodName,timestamp),dpi=200)
        #plt.show() #只有主线程才能处理该信号 -- ValueError: signal only works in main thread
    except (Exception),e:
        exc_type,exc_value,exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
        traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))

def manual_show_candlestick(target,periodName,data):
    """ 外部接口API: 手动绘图使用。
        periodName:周期名称的字符串（用于计算蜡烛图展示根数）
        data:行情数据库中dateframe结构的数据。
    """
    dataPicked = DataProcess.process_quotes_4indicator(periodName,data)

    # 均线
    ma = [0,]*len(Constant.MOVING_AVERAGE_LINE)
    for index,tag in zip(range(len(Constant.MOVING_AVERAGE_LINE)),Constant.MOVING_AVERAGE_LINE):
        ma[index] = MA.compute_sma(dataPicked['close'].as_matrix(),tag)

    # 布林线
    bbands = BollingerBands.compute_BBands(dataPicked['close'].as_matrix())

    show_candlestick(target,dataPicked,ma,bbands,periodName)
