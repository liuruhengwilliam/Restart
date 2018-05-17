#coding=utf-8

import platform
import sys
import os
import pandas as pd
from resource import Constant
from resource import Configuration
from quotation import QuotationKit
from indicator import CandleStick
from strategy.ClientMatch import ClientMatch
from strategy.Strategy import Strategy

"""
    辅助类：
    1.画图方法；
    2.历史数据分析；
"""
if __name__ == '__main__':
    choiceIndex = raw_input("Please choose:\n"+"  1.drawing picture of indicator\n"\
                            +"  2.analyse quote data in history\n"\
                            +"Your choice:\n")
    if choiceIndex == '1':
        filename = raw_input("file name input: ")
        tmName = raw_input("period name input:")
        if Constant.QUOTATION_DB_PREFIX.count(tmName) == 0:
            print "Error period name!"
            sys.exit()
        indx = Constant.QUOTATION_DB_PREFIX.index(tmName)
        if filename.find('.csv') != -1:
            dataWithId = pd.read_csv(filename)
            CandleStick.manual_show_candlestick(tmName,dataWithId)
        elif filename.find('.csv') != -1:
            CandleStick.manual_show_candlestick_withCSV(tmName,filename)
        else:
            print "Error file name input!"
    elif choiceIndex == '2':
        path = raw_input("Please input folder path WITH THE END OF '\\': ")
        if path=='':
            path = Configuration.get_working_directory()
        clientMatchHdl = ClientMatch()
        clientMatchHdl.match_KLineIndicator(path)
    else:
        print "Error choice!"
