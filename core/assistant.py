#coding=utf-8

import platform
import sys
import os
from resource import Primitive
from resource import Constant
from resource import Configuration
from quotation import QuotationKit
from indicator import CandleStick
from strategy.ClientMatch import ClientMatch

"""
    辅助类：
    1.db文件或db条目转换成csv文件的方法；
    2.画图方法；
"""
if __name__ == '__main__':
    choiceIndex = raw_input("Please choose:\n"+"  1.db translate to csv\n"\
                            +"  2.drawing plotting\n"\
                            +"  3.analyse KLine Indicator afterward\n"\
                            +"Your choice:\n")
    if choiceIndex == '1':
        filename = raw_input("file name input: ")
        cnt = raw_input("cnt to be translated: ")
        Primitive.translate_db_into_csv(filename,int(cnt))
    elif choiceIndex == '2':
        filename = raw_input("file name input: ")
        tmName = raw_input("period name input:")
        if Constant.QUOTATION_DB_PREFIX.count(tmName) == 0:
            print "Error period name!"
            sys.exit()
        indx = Constant.QUOTATION_DB_PREFIX.index(tmName)
        if filename.find('.db') != -1:
            dataWithId = Primitive.translate_db_to_df(filename)
            CandleStick.manual_show_candlestick(tmName,dataWithId)
        elif filename.find('.csv') != -1:
            CandleStick.manual_show_candlestick_withCSV(tmName,filename)
        else:
            print "Error file name input!"
    elif choiceIndex == '3':
        path = raw_input("folder path input: ")
        if path=='':
            path = Configuration.get_working_directory()
        clientMatchHdl = ClientMatch()
        clientMatchHdl.upate_afterwards_KLine_indicator(path)
    else:
        print "Error choice!"
