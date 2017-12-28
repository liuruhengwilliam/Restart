#coding=utf-8

import numpy as np
import MA
from resource import Constant

def compute_BBands(closePriceList):
    """ 外部接口API: 计算布林带。参考<< NumPy,3rd Edition.pdf >> P81
        closePriceList: close项价格列表
        返回值： 布林带上轨/中轨/下轨
    """
    N = Constant.BOLLINGER_BANDS
    weights = np.ones(N)/N
    sma = MA.compute_sma(closePriceList,N)

    deviation = []
    C = len(closePriceList)

    for i in range(N-1, C):
        if i+N < C:
            dev = closePriceList[i:i+N]
        else:
            dev = closePriceList[-N:]
        averages = np.zeros(N)
        averages.fill(sma[i-N-1])
        dev = dev-averages
        dev = dev**2
        dev = np.sqrt(np.mean(dev))
        deviation.append(dev)

    deviation = 2*np.array(deviation)
    upperBB = sma + deviation
    lowerBB = sma - deviation

    return upperBB,sma,lowerBB

