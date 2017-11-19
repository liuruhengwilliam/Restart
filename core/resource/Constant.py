#coding=utf-8

import time
import datetime

# 数据抓取模块应该设定在每周一凌晨6点开始启动。这样能够兼顾到各周期记录（不遗漏）。
# 软件版本，行业相关术语等定义
VERSION_CODE = 'V0.5.0'
def get_version_info():
    """ 外部接口API: """
    return VERSION_CODE+"\n"+"Build Time: %s"%time.strftime("%Y-%m-%d %H:%M",time.localtime())

# 夏令时(Daylight saving time)和冬令时(standard time)
# 夏令时定义：3月最后一个星期日开始，10月最后一个星期日结束。
# time类中"tm_isdst"貌似有点水土不服！
# 夏令时每日结算时间:5点到6点(6点整开盘)
DAYLIGHT_SETTLEMENT_HOUR_TIME=5

# 冬令时每日结算时间:6点到7点(7点整开盘)
STANDARD_SETTLEMENT_HOUR_TIME=6


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
    if(int(day) == 6 and int(hour) >= STANDARD_SETTLEMENT_HOUR_TIME) or int(day) == 7:
        return True
    return False

def exit_on_weekend(workWeek):
    """ 到周末就退出 """
    curWeek = (datetime.datetime.now()).strftime('%U')
    if curWeek != workWeek:
        return True

    return is_weekend()