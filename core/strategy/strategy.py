#coding=utf-8

import talib
import numpy as np
import pandas as pd

from quotation import QuotationKit

"""
    策略算法模块：提供策略算法接口API
"""

def talib_func():
    func_collection = talib.get_functions()
    for i in func_collection:
        print i

    func_dict = talib.get_function_groups()
    # 迭代器
    for item in func_dict.iteritems():
        print item

def numpy_data():
    data_analyse = numpy.random.random(10)
    print type(data_analyse)

def talib_sma_test():
    data_analyse = {
        'open':numpy.random.random(100),
        'high':numpy.random.random(100),
        'low':numpy.random.random(100),
        'close':numpy.random.random(100),
        'volume':numpy.random.random(100)
    }
    #close = numpy.random.random(100)
    #output = talib.SMA(close)
    output = talib.abstract.SMA(data_analyse, timeperiod=20, price='open')
    print (output)

