#coding=utf-8

import sys
import datetime
import traceback
import StrategyMisc
from resource import Constant
from resource import Trace
from resource import Configuration

def update_strategy(dfStrategy,currentInfo):
    """ 外部接口API: 更新某周期的策略盈亏率数据。更新高阶定时器周期的SER数据。
        target:标的字符串
        currentInfo:当前时间和价格信息
    """
    closeTimeStr, highPrice, lowPrice = currentInfo#当前时间和价格信息
    # 杂项处理
    if closeTimeStr.find('/')!=-1:
        closeTimeStr = closeTimeStr.replace('/','-')
    if len(closeTimeStr.split(':')) == 2:
        closeTime = datetime.datetime.strptime(closeTimeStr,"%Y-%m-%d %H:%M")
    else:
        closeTime = datetime.datetime.strptime(closeTimeStr,"%Y-%m-%d %H:%M:%S")

    if highPrice == 0.0 or lowPrice == 0.0:#对于抓取的异常数据不做处理
        return

    dfStrategy.is_copy = False

    for rowNo,itemRow in zip(dfStrategy.index,dfStrategy.itertuples(index=False)):
        # 超过计时跨度不做处理
        if itemRow[-2] >= Constant.SER_MAX_PERIOD:#最小周期从0开始计数故不能取MAX值。
            continue

        # time项的异常处理
        baseTime = itemRow[Constant.SER_DF_STRUCTURE.index('time')]
        if baseTime.find('/')!=-1:
            baseTime = baseTime.replace('/','-')
        if len(baseTime.split(':')) == 2:
            baseTimeDT = datetime.datetime.strptime(baseTime,"%Y-%m-%d %H:%M")
        else:
            baseTimeDT = datetime.datetime.strptime(baseTime,"%Y-%m-%d %H:%M:%S")

        #不更新过期（相对于策略盈亏条目的生成时间）的收盘价格。入参closeTime是datetime类型
        if closeTime < baseTimeDT:
            continue
        try:
            basePrice = itemRow[Constant.SER_DF_STRUCTURE.index('price')]
            patternStr = itemRow[Constant.SER_DF_STRUCTURE.index('patternName')]
            dirc = itemRow[Constant.SER_DF_STRUCTURE.index('patternVal')]
            deadTimeIndx = Constant.SER_DF_STRUCTURE.index('DeadTime')
            #'M15maxEarn'为记录项基址,itemRow[-2]*4为偏移量--链式定时序号。每四个记录项为一组。
            XmaxEarnIndx = int(Constant.SER_DF_STRUCTURE.index('M15maxEarn'))+int(itemRow[-2]*4)
            XmaxEarnTMIndx = XmaxEarnIndx+1
            XmaxLossIndx = XmaxEarnIndx+2
            XmaxLossTMIndx = XmaxEarnIndx+3
            #注：Pandas元组中开头有自带Index项，所以下标有别于DataFrame结构。
            #比对并更新（若需要）极值
            #itemRow为Pandas元组，开头自带Index项，所以下标要加一。也可以通过index=False去掉最开头的索引。
            if itemRow[XmaxEarnIndx]==0 or itemRow[XmaxLossIndx]==10000:#初始条目
                if dirc > 0:#‘多’方向
                    dfStrategy.ix[rowNo,[XmaxEarnIndx,XmaxEarnTMIndx,XmaxLossIndx,XmaxLossTMIndx]]\
                        = [highPrice,closeTimeStr,lowPrice,closeTimeStr]
                else:#‘空’方向
                    dfStrategy.ix[rowNo,[XmaxEarnIndx,XmaxEarnTMIndx,XmaxLossIndx,XmaxLossTMIndx]]\
                        = [lowPrice,closeTimeStr,highPrice,closeTimeStr]
            else:
                if dirc > 0:#‘多’方向
                    if highPrice > itemRow[XmaxEarnIndx]:#大于最大盈利值
                        dfStrategy.ix[rowNo,[XmaxEarnIndx,XmaxEarnTMIndx]] = [highPrice,closeTimeStr]
                    if lowPrice < itemRow[XmaxLossIndx]:#小于最大亏损值
                        dfStrategy.ix[rowNo,[XmaxLossIndx,XmaxLossTMIndx]] = [lowPrice,closeTimeStr]
                else:#‘空’方向 -- maxEarn值小于maxLoss值
                    if lowPrice<itemRow[XmaxEarnIndx]:#大于最大盈利值
                        dfStrategy.ix[rowNo,[XmaxEarnIndx,XmaxEarnTMIndx]] = [lowPrice,closeTimeStr]
                    if highPrice>itemRow[XmaxLossIndx]:#小于最大亏损值
                        dfStrategy.ix[rowNo,[XmaxLossIndx,XmaxLossTMIndx]] = [highPrice,closeTimeStr]

            #判断是否止损，止损刻度时间的精度是5min。
            if itemRow[deadTimeIndx] == '1900-01-01 00:00:00' and \
                            StrategyMisc.set_dead_price(basePrice,dirc,highPrice,lowPrice) == True:
                dfStrategy.ix[rowNo,deadTimeIndx] = closeTimeStr
                Trace.output('warn','It die following item:'+' '.join(list(dfStrategy.ix[rowNo].astype(str))))

            #链式定时计数小于等于0说明有相关周期策略盈亏率统计周期要增加
            if itemRow[-1] <= Constant.CHAIN_PERIOD[0]:
                periodIndx = int(itemRow[-2]+1) #链式定时的下个周期序号
                #设置计数初值。需要减去前一个周期数值。
                baseAddr = Constant.QUOTATION_DB_PERIOD.index(15*60)#周期计数值的基址
                dfStrategy.ix[rowNo,[-2,-1]] = [periodIndx,Constant.QUOTATION_DB_PERIOD[baseAddr+periodIndx]]
            else:#链式计数还未到期
                dfStrategy.ix[rowNo,-1] -= Constant.CHAIN_PERIOD[0]
            #print "update the following:\n",dfStrategy.ix[rowNo]#调试点
        except (Exception),e:
            exc_type,exc_value,exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))

    return dfStrategy