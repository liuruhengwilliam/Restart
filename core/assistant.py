#coding=utf-8

import platform
import sys
import os
from resource import Constant
from quotation import QuotationKit
from drawing import DrawingKit

"""
    辅助类：
    1.db文件或db条目转换成csv文件的方法；
    2.画图方法；
"""
if __name__ == '__main__':
    choiceIndex = raw_input("Please choose:\n"+"1.db translate to csv\n"+"2.drawing plotting\n"+"Your choice:\n")
    if choiceIndex == '1':
        filename = raw_input("file name input: ")
        cnt = raw_input("cnt to be translated: ")
        QuotationKit.translate_db_into_csv(filename,int(cnt))
    elif choiceIndex == '2':
        filename = raw_input("file name input: ")
        tmName = raw_input("period name input:")
        if Constant.QUOTATION_DB_PREFIX.count(tmName) == 0:
            print "Error period name!"
            sys.exit()
        indx = Constant.QUOTATION_DB_PREFIX.index(tmName)
        if filename.find('.db') != -1:
            dataWithId = QuotationKit.translate_db_to_df(filename)
            DrawingKit.show_period_candlestick(tmName,dataWithId,isDraw=True)
        elif filename.find('.csv') != -1:
            DrawingKit.show_period_candlestick_withCSV(tmName,filename,isDraw=True)
        else:
            print "Error file name input!"
    else:
        print "Error choice!"
