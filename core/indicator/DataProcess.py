#coding=utf-8

import os
import platform
import datetime
import numpy as np
from matplotlib.dates import date2num
from resource import Constant
from resource import Trace
from resource import Configuration

def process_xaxis_labels(periodIndx, tmList):
    """ 外部接口API：生成X轴的标签字符串列表
        periodIndx: 对应周期列表的列表下标
        tmList: 时间列表
        返回值：标签字符串列表
    """
    labelsList = []
    scale = Constant.SCALE_CANDLESTICK[periodIndx]

    if  scale == Constant.BIG_SCALE_STAGE:
        labelsList = map(lambda x:(x.split(' ')[0]).split('-')[1]+'-'+(x.split(' ')[0]).split('-')[2],\
            [tm for tm in tmList])
    elif scale == Constant.MEDIUM_SCALE_STAGE:
        labelsList = map(lambda x:(x.split(' ')[0]).split('-')[1]+'-'+(x.split(' ')[0]).split('-')[2]+\
            ' '+(x.split(' ')[1]).split(':')[0]+':'+(x.split(' ')[1]).split(':')[1],[tm for tm in tmList])
    else:
        labelsList = map(lambda x:(x.split(' ')[1]).split(':')[0]+':'+(x.split(' ')[1]).split(':')[1],\
            [tm for tm in tmList])

    return labelsList

def process_compact_dt2num(periodIndx, dt2numList):
    """ 内部接口API：dt2num列调整（去掉结算时间的空档）。
        从而达到绘制蜡烛图时X-轴ticks连续的目的，便于观察和追溯。
        periodIndx: 定时器列表中的下标
        dt2numList: dt2num的列表数据结构入参
        返回值：调整dt2num之后的列表数据结构。
    """
    # 补偿差值列表次序同列表Constant.QUOTATION_DB_PREFIX顺序。各周期补偿差值为统计算术平均值，非精确值。
    deltaTickList = [0,0.0035,0.0104,0.0208,0.0417,0.0833,0.1666,0.2500,0.5000,1.0000,7.0000]
    for indx,subValue in enumerate(np.array(dt2numList[1:])-np.array(dt2numList[:-1])):
        if subValue >= 1.5*deltaTickList[periodIndx]:#允许有50%误差
            #超出该值则认为出现时间缺口，需要调整数据。从此节点至末尾都要调整。
            dt2numList[indx+1:]-=np.array([subValue-deltaTickList[periodIndx]]*len(dt2numList[indx+1:]))

def process_quotes_4indicator(period,data):
    """ 外部接口API：处理quotes数据。调用date2num函数转换datetime。
        data: dataframe结构的数据
        返回值: dateframe结构数据(period, time, open, high, low, close, dt2num)
    """
    dataCnt = len(data)
    necessaryCnt = Constant.CANDLESTICK_PERIOD_CNT[Constant.QUOTATION_DB_PREFIX.index(period)]

    if dataCnt >= necessaryCnt:
        dataSupplement = data.iloc[-necessaryCnt:]#取出最近(倒数)的规定数目的条目
    else:
        dataSupplement = data

    # 附加'dt2num'列
    dateDeal = []
    for tm in np.array(dataSupplement['time']):
        if tm.find('/')!=-1:
            tm = tm.replace('/','-')
        if len(tm.split(':')) == 2:
            dateDeal.append(date2num(datetime.datetime.strptime(tm,"%Y-%m-%d %H:%M")))
        else:
            dateDeal.append(date2num(datetime.datetime.strptime(tm,"%Y-%m-%d %H:%M:%S")))

    #print "Before adjusted:",dateDeal,(np.array(dateDeal[1:])-np.array(dateDeal[:-1]))#调试点
    # 为绘图时将空白时间删除，调整DataFrame中的‘dt2num’列
    process_compact_dt2num(Constant.QUOTATION_DB_PREFIX.index(period),dateDeal)
    #print "After adjusted:",dateDeal,(np.array(dateDeal[1:])-np.array(dateDeal[:-1]))#调试点
    dataSupplement.is_copy = False
    dataSupplement['dt2num']=dateDeal
    return dataSupplement