#coding=utf-8

import platform
import sys
import os
#from resource import Configuration
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
        QuotationKit.translate_db_into_csv(file,int(cnt))
    elif choiceIndex == '2':
        filename = raw_input("file name input: ")
        period = raw_input("period choice: ")
        DrawingKit.show_period_candlestick(filename,period)
    else:
        print "Error choice!"
