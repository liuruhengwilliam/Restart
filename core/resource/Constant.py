#coding=utf-8
import os
import sys
import time
import datetime
import platform
import threading
import Trace
#=================================================================================
# 数据抓取模块应该设定在每周一凌晨6点开始启动。这样能够兼顾到各周期记录（不遗漏）。
# 软件版本，行业相关术语等定义
# 月份和日期对应码
MONTH_CODE = ('A','B','C','D','E','F','G','H','I','J','K','L')
DAY_CODE = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N',\
             'O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e')

def get_date_code():
    """ 返回月份和日期对应的字母码 """
    dt = datetime.datetime.now()
    month,day = dt.strftime('%m'),dt.strftime('%d')
    return MONTH_CODE[int(month)-1]+DAY_CODE[int(day)-1]

VERSION_CODE = 'V0.6.3'
def get_version_info():
    """ 内/外部接口API: """
    return VERSION_CODE + get_date_code() + "\n" + \
           "Build Time: %s"%time.strftime("%Y-%m-%d %H:%M",time.localtime())

def envi_init():
    """ 初始化环境变量、程序抬头信息等相关内容
    """
    Trace.output('info',get_version_info())
    if (platform.system() == "Linux"):
        sys.path.append(os.getcwd()+'/quotation')
        sys.path.append(os.getcwd()+'/resource')
        sys.path.append(os.getcwd()+'/engine')
        sys.path.append(os.getcwd()+'/timer')

# =========================================================================================
# 蜡烛图相关
CANDLESTICK_DEFAULT_CNT = 200 # 每张蜡烛图片文件默认展示200根K线
# =========================================================================================
# https://www.ricequant.com/community/topic/2393/
# K线组合形态
STRATEGY_CANDLESTICK = ('CDL2CROWS','CDL3BLACKCROWS','CDL3INSIDE','CDL3LINESTRIKE','CDL3OUTSIDE','CDL3STARSINSOUTH',\
                        'CDL3WHITESOLDIERS','CDLABANDONEDBABY','CDLADVANCEBLOCK','CDLBELTHOLD','CDLBREAKAWAY',\
                        'CDLCLOSINGMARUBOZU','CDLCONCEALBABYSWALL','CDLCOUNTERATTACK','CDLDARKCLOUDCOVER',\
                        'CDLDOJI','CDLDOJISTAR','CDLDRAGONFLYDOJI','CDLENGULFING','CDLEVENINGDOJISTAR',\
                        'CDLEVENINGSTAR','CDLGAPSIDESIDEWHITE','CDLGRAVESTONEDOJI','CDLHAMMER','CDLHANGINGMAN',\
                        'CDLHARAMI','CDLHARAMICROSS','CDLHIGHWAVE','CDLHIKKAKE','CDLHIKKAKEMOD','CDLHOMINGPIGEON',\
                        'CDLIDENTICAL3CROWS','CDLINNECK','CDLINVERTEDHAMMER','CDLKICKING','CDLKICKINGBYLENGTH',\
                        'CDLLADDERBOTTOM','CDLLONGLEGGEDDOJI','CDLLONGLINE','CDLMARUBOZU','CDLMATCHINGLOW',\
                        'CDLMATHOLD','CDLMORNINGDOJISTAR','CDLMORNINGSTAR','CDLONNECK','CDLPIERCING','CDLRICKSHAWMAN',\
                        'CDLRISEFALL3METHODS','CDLSEPARATINGLINES','CDLSHOOTINGSTAR','CDLSHORTLINE','CDLSPINNINGTOP',\
                        'CDLSTALLEDPATTERN','CDLSTICKSANDWICH','CDLTAKURI','CDLTASUKIGAP','CDLTHRUSTING','CDLTRISTAR',\
                        'CDLUNIQUE3RIVER','CDLUPSIDEGAP2CROWS','CDLXSIDEGAP3METHODS')
# 均线
STRATEGY_MEANLINE = ()
#=================================================================================
# 行情数据库中记录项
QUOTATION_STRUCTURE = ('time','open','high','low','close')

#循环定时器周期
# 行情数据库记录项周期: 6sec(不生成db文件),5min,15min,30min,1hour,2hour,4hour,6hour,12hour,1day,1week
QUOTATION_DB_PREFIX = ('6sec','5min','15min','30min','1hour','2hour','4hour','6hour','12hour','1day','1week')
QUOTATION_DB_PERIOD = (6,5*60,15*60,30*60,1*3600,2*3600,4*3600,6*3600,12*3600,24*3600,5*24*3600)
# 日线和周线定时器周期时间调整（日线需减去每日的结算时间，周线需减去周六闭市时间差） 2017-11-02

#链式定时器周期
CHAIN_PERIOD = (1800,1*3600-1800,2*3600-1*3600,4*3600-2*3600,6*3600-4*3600,\
                12*3600-6*3600,24*3600-12*3600,24*5*3600-24*3600)

UPDATE_PERIOD_FLAG = [True]*len(QUOTATION_DB_PERIOD)
#=====================================================================================
# 夏令时(Daylight saving time)和冬令时(standard time)
# 夏令时定义：3月最后一个星期日开始，10月最后一个星期日结束。
# time类中"tm_isdst"貌似有点水土不服！
# 夏令时每日结算时间:5点到6点(6点整开盘)
DAYLIGHT_SETTLEMENT_HOUR_TIME=5
SAT_DAYLIGHT_SETTLEMENT_HOUR_TIME=3
# 冬令时每日结算时间:6点到7点(7点整开盘)
STANDARD_SETTLEMENT_HOUR_TIME=6
SAT_STANDARD_SETTLEMENT_HOUR_TIME=3

def is_standard_time():
    """当前时间是否属于冬令时"""
    return True
    #return False

def is_closing_market():
    """ 外部接口API:判断当前时间是否为闭市时间 """
    # 每工作日凌晨5点到6点为结算时间
    hour = time.strftime("%H",time.localtime())

    if is_standard_time() == True:#冬令时
        if int(hour) == STANDARD_SETTLEMENT_HOUR_TIME:
            return True
    else:#夏令时
        if int(hour) == DAYLIGHT_SETTLEMENT_HOUR_TIME:
            return True

    return False

def is_weekend():
    """ 是否周末---周末闭市 """
    now = datetime.datetime.now()
    day, hour = now.isoweekday(),now.strftime("%H")
    if(int(day) == 6 and int(hour) > SAT_STANDARD_SETTLEMENT_HOUR_TIME) or int(day) == 7:
        return True
    return False

def exit_on_weekend(workWeek):
    """ 到周末就退出 """
    curWeek = (datetime.datetime.now()).strftime('%U')
    if curWeek != workWeek:
        return True

    return is_weekend()