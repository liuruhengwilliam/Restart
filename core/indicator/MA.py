#coding=utf-8

import numpy as np

def compute_sma(closePriceList, smaPeriod):
    """ 外部接口API: 根据close价格计算该周期的算术平均线
        closePriceList: close项价格列表
        smaPeriod: 均线名称的整数数值。比如：5、10、30、100、200等。
    """
    N = smaPeriod
    weights = np.ones(N)/N
    # 参见<< NumPy,3rd Edition.pdf >> P77
    return np.convolve(weights, closePriceList)[N-1:-N+1]

