#coding=utf-8

import datetime

from resource import Configuration
from resource import Constant
from resource import Trace
from indicator import DataProcess
import talib
import numpy as np
import matplotlib.pyplot as plt
import traceback
import sys

def MACD():
    """MACD指标绘制初探"""
    dataWithId = np.read_cdv("D:\\misc\\2018-05\\15min\\15min-quote.csv")
    close = np.array(dataWithId['close'])
    #三个返回值的意义研究
    macd,macdsignal,macdhist = talib.MACD(close,fastperiod=12,slowperiod=26,signalperiod=9)
    print '==== macd ====\n',macd
    print '\n==== macdsignal ====\n',macdsignal
    print '\n==== macdhist ====\n',macdhist

    dataPicked = DataProcess.process_quotes_4indicator('15min',dataWithId)
    quotes = np.array(dataPicked[['dt2num','open','high','low','close']])
    fig, ax = plt.subplots(figsize=(20,10))
    fig.subplots_adjust(bottom=0.2)

    try:
        ax.set_xlim([quotes.item(0,0),quotes.item(-1,0)])
        plt.plot(dataPicked['dt2num'].as_matrix()[16:],macdsignal,'r',ls='--',label='MACD_dif')
        plt.plot(dataPicked['dt2num'].as_matrix()[16:],macdhist,'y',ls='--',label='MACD_dea')
        plt.legend(loc='upper left')
        plt.show()
    except (Exception),e:
        exc_type,exc_value,exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
        traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))

