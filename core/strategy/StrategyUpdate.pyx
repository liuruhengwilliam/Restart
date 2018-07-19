#coding=utf-8

import sys
import datetime
import traceback
from resource import Constant
from resource import Trace
from resource import Configuration

def set_dead_price(basePrice,dirc,highPrice,lowPrice):
    """外部接口API:检测价格是否超过止损线
       如果超过，返回True；否则返回False。
    """
    if dirc > 0:#“多”方向
        if float(lowPrice) > float(basePrice):
            return False
        deltaPrice = float(basePrice) - float(lowPrice)
    else:#“空”方向
        if float(basePrice) > float(highPrice):
            return False
        deltaPrice = float(highPrice) - float(basePrice)

    if deltaPrice/float(basePrice) >= Constant.STOP_LOSS_RATE:
        return True
    else:
        return False

def update_strategy(dfStrategy,currentInfo):
    """ 外部接口API: 更新某周期的策略盈亏率数据。更新高阶定时器周期的SER数据。
        target:标的字符串
        currentInfo:当前时间和价格信息
    """
    closeTimeStr, highPrice, lowPrice = currentInfo#当前时间和价格信息
    if highPrice == 0.0 or lowPrice == 0.0:#对于抓取的异常数据不做处理
        return dfStrategy
    # 杂项处理
    if closeTimeStr.find('/')!=-1:
        closeTimeStr = closeTimeStr.replace('/','-')

    #后续展开的itemRow为Pandas元组，开头自带Index项，所以下标要加一。也可以通过index=False去掉最开头的索引。
    basePriceIndx = Constant.SER_DF_STRUCTURE.index('price')+1
    dirctionIndx = Constant.SER_DF_STRUCTURE.index('patternVal')+1
    deadTimeIndx = Constant.SER_DF_STRUCTURE.index('DeadTime')+1

    dfStrategy.is_copy = False
    for indx in set(dfStrategy['tmChainIndx']):#依据周期序列处理
        if indx >= Constant.SER_MAX_PERIOD:#最小周期从0开始计数故不能取MAX值。
            continue
        #'M15maxEarn'为记录项基址,itemRow[-2]*4为偏移量--链式定时序号。每四个记录项为一组。
        #注：Pandas元组中开头有自带Index项，所以下标有别于DataFrame结构。
        XmaxEarnIndx = int(Constant.SER_DF_STRUCTURE.index('M15maxEarn')+1)+int(indx*4)
        XmaxEarnTMIndx = XmaxEarnIndx+1
        XmaxLossIndx = XmaxEarnIndx+2
        XmaxLossTMIndx = XmaxEarnIndx+3

        for itemRow in dfStrategy[dfStrategy['tmChainIndx']==indx].itertuples():#itemRow[0]就是在dfStrategy中的行号
            try:
                basePrice = itemRow[basePriceIndx]
                dirc = itemRow[dirctionIndx]
                #比对并更新（若需要）极值
                if dirc > 0:#‘多’方向
                    if highPrice > itemRow[XmaxEarnIndx]:#大于最大盈利值
                        dfStrategy.ix[itemRow[0],[XmaxEarnIndx,XmaxEarnTMIndx]] = [highPrice,closeTimeStr]
                    if lowPrice < itemRow[XmaxLossIndx]:#小于最大亏损值
                        dfStrategy.ix[itemRow[0],[XmaxLossIndx,XmaxLossTMIndx]] = [lowPrice,closeTimeStr]
                else:#‘空’方向 -- maxEarn值小于maxLoss值
                    if lowPrice < itemRow[XmaxEarnIndx]:#大于最大盈利值
                        dfStrategy.ix[itemRow[0],[XmaxEarnIndx,XmaxEarnTMIndx]] = [lowPrice,closeTimeStr]
                    if highPrice > itemRow[XmaxLossIndx]:#小于最大亏损值
                        dfStrategy.ix[itemRow[0],[XmaxLossIndx,XmaxLossTMIndx]] = [highPrice,closeTimeStr]

                #判断是否止损，止损刻度时间的精度是5min。
                if itemRow[deadTimeIndx]=='1900-01-01 00:00:00' and set_dead_price(basePrice,dirc,highPrice,lowPrice)==True:
                    dfStrategy.ix[itemRow[0],deadTimeIndx] = closeTimeStr
                    Trace.output('warn','It die following item:'+' '.join(list(dfStrategy.ix[itemRow[0]].astype(str))))

                #链式定时计数小于等于0说明有相关周期策略盈亏率统计周期要增加
                if itemRow[-1] <= Constant.CHAIN_PERIOD[0]:
                    #链式定时的下个周期序号+周期计数值的基址
                    periodIndx = int(indx+1+Constant.QUOTATION_DB_PERIOD.index(15*60))
                    dfStrategy.ix[itemRow[0],[-2,-1]] = [indx+1,Constant.QUOTATION_DB_PERIOD[periodIndx]]
                else:#链式计数还未到期
                    dfStrategy.ix[itemRow[0],-1] -= Constant.CHAIN_PERIOD[0]
                #print "update the following:\n",dfStrategy.ix[itemRow[0]]#调试点
            except (Exception),e:
                exc_type,exc_value,exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_tb)
                traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))

    return dfStrategy