#coding=utf-8

import os
import datetime
import platform
import threading

#================================================================================
# 月份和日期对应码
MONTH_CODE = ('A','B','C','D','E','F','G','H','I','J','K','L')
DAY_CODE = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N',\
             'O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e')

def get_date_code():
    """ 返回月份和日期对应的字母码 """
    dt = datetime.datetime.now()
    month,day = dt.strftime('%m'),dt.strftime('%d')
    return MONTH_CODE[int(month)-1]+DAY_CODE[int(day)-1]

#=================================================================================
# 行情数据库中记录项
QUOTATION_STRUCTURE = ('open','high','low','close','time')

#循环定时器周期
# 行情数据库记录项周期: 6sec(不生成db文件),5min,15min,30min,1hour,2hour,4hour,6hour,12hour,1day,1week
QUOTATION_DB_PREFIX = ('6sec','5min','15min','30min','1hour','2hour','4hour','6hour','12hour','1day','1week')
QUOTATION_DB_PERIOD = (6,5*60,15*60,30*60,1*3600,2*3600,4*3600,6*3600,12*3600,(24-1)*3600,(5*24-1)*3600)
# 日线和周线定时器周期时间调整（日线需减去每日的结算时间，周线需减去周六闭市时间差） 2017-11-02

#链式定时器周期
CHAIN_PERIOD = (1800,1*3600-1800,2*3600-1*3600,4*3600-2*3600,6*3600-4*3600,\
                12*3600-6*3600,24*3600-12*3600,24*5*3600-24*3600)

UPDATE_PERIOD_FLAG = [True]*len(QUOTATION_DB_PERIOD)
UPDATE_LOCK = [threading.RLock()]*len(QUOTATION_DB_PERIOD)

#=====================================================================================
DIR_PATH = None
def get_working_directory():
    """内/外部接口API：获取当前周工作目录"""
    # 寻找当前周数并生成文件名前缀
    dt = datetime.datetime.now()
    year,week = dt.strftime('%Y'),dt.strftime('%U')
    fileNamePrefix = year+'-'+week

    #生成文件路径(依据不同操作系统)
    sysName = platform.system()
    if (sysName == "Windows"):
        DIR_PATH = 'D:/misc/future/'+fileNamePrefix
    elif (sysName == "Linux"):
        DIR_PATH = '~/mess/future/'+fileNamePrefix
    else :# 未知操作系统
        DIR_PATH = fileNamePrefix

    if not os.path.exists(DIR_PATH):
        # 创建当周数据库文件夹
        os.makedirs(DIR_PATH)

    return DIR_PATH
