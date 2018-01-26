#coding=utf-8

import os
import platform
import datetime
import numpy as np
from matplotlib.dates import date2num
from resource import Constant
from quotation import QuotationKit
from resource import Trace

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

def process_compact_dt2num(periodIndx, dataPicked):
    """ 内部接口API：dt2num列调整（去掉结算时间的空档）。
        从而达到绘制蜡烛图时X-轴ticks连续的目的，便于观察和追溯。
        periodIndx: 定时器列表中的下标
        dataPicked: DataFrame数据结构入参
        返回值：调整dt2num列之后的DataFrame数据结构。
    """
    deltaID = 0
    dt2numEx = .0 #'dt2num'前值
    supplementFlag = False #数据是否补全的标志
    # 补偿差值列表次序同列表Constant.QUOTATION_DB_PREFIX顺序。各周期补偿差值为统计算术平均值，非精确值。
    deltaTickList = [0,0.0035,0.0104,0.0208,0.0417,0.0833,0.1666,0.2500,0.5000,1.0000,7.0000]
    for indx in dataPicked.index:
        idCursor = int(dataPicked.loc[indx,['id']])
        if deltaID == 0:#初次检测
            deltaID = idCursor-indx #设置序号偏差初值
        if deltaID != int(idCursor-indx):#出现补全数据（有时间缺口）
            supplementFlag = True #设置补全标志，后面每行的'dt2num'项都要调整。
        if supplementFlag == True: #调整'dt2num'项
            dataPicked.loc[indx,['dt2num']] = dt2numEx + deltaTickList[periodIndx] #调整后回写

        dt2numEx = float(dataPicked.loc[indx,['dt2num']]) #记录'dt2num'前值

def process_quotes_4indicator(periodName,dataWithID):
    """ 外部接口API：处理quotes数据
        1.去掉id栏
        2.调用date2num函数转换datetime
        periodName:周期名称的字符串
        dataWithID: dataframe结构的数据
        返回值: dateframe结构数据(id, time, open, high, low, close, dt2num)
    """
    dataCnt = dataWithID.iloc[-1:]['id']
    indx = Constant.QUOTATION_DB_PREFIX.index(periodName)
    gap = int(dataCnt)-Constant.CANDLESTICK_PERIOD_CNT[indx]
    if gap >= 0:
        # 取从第（dataCnt-X个）到最后一个（第dataCnt）的数据（共X个）
        dataSupplementWithID = dataWithID.ix[int(gap):]
    else:# 要补齐蜡烛图中K线数目
        dataSupplementWithID = QuotationKit.supplement_quotes(periodName,dataWithID,int(abs(gap)))

    dataSupplementWithID.is_copy = False #消除告警信息
    # 附加'dt2num'列
    dateDeal = []
    for tm in np.array(dataSupplementWithID['time']):
        if type(tm) == unicode:#unicode需要转string
            dateDeal.append(date2num(datetime.datetime.strptime(tm.encode('unicode-escape'),"%Y-%m-%d %H:%M:%S")))
        elif type(tm) == str:
            dateDeal.append(date2num(datetime.datetime.strptime(tm,"%Y-%m-%d %H:%M:%S")))
        else:#Just joke: default would be the type of datetime.datetime
            dateDeal.append(date2num(tm))

    dataSupplementWithID['dt2num'] = (dateDeal)

    # 为绘图时将空白时间删除，调整DataFrame中的‘dt2num’列
    process_compact_dt2num(indx, dataSupplementWithID)

    return dataSupplementWithID