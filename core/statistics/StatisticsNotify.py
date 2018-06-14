#coding=utf-8

"""
    通知相关的函数
"""

from resource import Constant
from resource import Configuration

def write_abstract(indicator,strAbstract):
    """ 内部接口API: 各指标的指示摘要说明字符串存档函数
            strAbstract: 待写入的摘要字符串
    """
    filePath = Configuration.get_working_directory()+'abstract.txt'

    fd = open(filePath,'a+')
    fd.write(Constant.ABSTRACT_TITLE[indicator])
    if indicator == 'KLine':
        fd.write(' %s'%strAbstract)
        # 对于别的指标，可写入其他信息：MA--趋势；MACD--金叉/死叉；BBand--压力/支撑位等

    fd.write('\n')
    fd.write(strAbstract)
    fd.close()

def read_abstract():
    """ 内部接口API: 各指标的指示摘要说明字符串读档函数 """

