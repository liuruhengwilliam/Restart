#coding=utf-8

import platform
import sys
import os
#from resource import Configuration
from quotation import QuotationKit

"""
    辅助类：
    1.db文件或db条目转换成csv文件的方法；
    2.画图方法；
"""

def db_to_csv(file,cnt):
    """ db文件转换成csv文件的工具函数
        file: db文件名（含文件路径）。raw_input方式接收控制台输入，字符串类型。
        cnt: 带转换db条目的行数。raw_input方式接收控制台输入，字符串类型，且-1为全部转换。
    """
    QuotationKit.translate_db_into_csv(file,int(cnt))

if __name__ == '__main__':
    choiceIndex = raw_input("Please choose:\n"+"1.db translate to csv\n"+"2.drawing plotting\n"+"Your choice:\n")
    if choiceIndex == '1':
        filename = raw_input("file name input: ")
        cnt = raw_input("cnt to be translated: ")
        db_to_csv(filename,cnt)
    else:
        print("drawing")
