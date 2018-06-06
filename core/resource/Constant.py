#coding=utf-8
import re
import os
import sys
import time
import datetime
import platform
import threading
import Trace
import Configuration
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

VERSION_CODE = 'V2.1.1Q'
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

#止损率定义。波动超过基础价格的10%。
STOP_LOSS_RATE = 0.1
# =========================================================================================
# 蜡烛图相关
# 各种周期的尺度定义
LITTEL_SCALE_STAGE = 0
SMALL_SCALE_STAGE = 1
MEDIUM_SCALE_STAGE = 2
BIG_SCALE_STAGE = 3

LITTEL_SCALE_CANDLESTICK = (0,)
SMALL_SCALE_CANDLESTICK = (1,)
MEDIUM_SCALE_CANDLESTICK = (2,)
BIG_SCALE_CANDLESTICK = (3,)
SCALE_CANDLESTICK = (LITTEL_SCALE_CANDLESTICK*2+SMALL_SCALE_CANDLESTICK*2+\
                     MEDIUM_SCALE_CANDLESTICK*4+BIG_SCALE_CANDLESTICK*3)
# 展示蜡烛图的默认尺度
DEFAULT_SCALE_CANDLESTICK_SHOW = 4 #小时级别之上的周期绘制指标图形
# #从效率的角度考虑，服务端不再绘制指标图形，改由客户端定时绘制。

LITTLE_SCALE_CANDLESTICK_DEFAULT_CNT = (0,) # 微尺度时间周期的蜡烛图默认数目
SMALL_SCALE_CANDLESTICK_DEFAULT_CNT = (150,) # 小尺度时间周期的蜡烛图默认数目
MEDIUM_SCALE_CANDLESTICK_DEFAULT_CNT = (150,) # 中尺度时间周期的蜡烛图默认数目
BIG_SCALE_CANDLESTICK_DEFAULT_CNT = (180,) # 大尺度时间周期的蜡烛图默认数目
# 按照周期定时器的次序定义尺度
CANDLESTICK_PERIOD_CNT = (LITTLE_SCALE_CANDLESTICK_DEFAULT_CNT*1 + \
                          SMALL_SCALE_CANDLESTICK_DEFAULT_CNT*3 + \
                          MEDIUM_SCALE_CANDLESTICK_DEFAULT_CNT*4 + \
                          BIG_SCALE_CANDLESTICK_DEFAULT_CNT*3)
# =========================================================================================
# https://www.ricequant.com/community/topic/2393/
# K线组合形态
CANDLESTICK_PATTERN = ('CDL2CROWS','CDL3BLACKCROWS','CDL3INSIDE','CDL3LINESTRIKE','CDL3OUTSIDE',\
    'CDL3STARSINSOUTH','CDL3WHITESOLDIERS','CDLABANDONEDBABY','CDLADVANCEBLOCK','CDLBELTHOLD',\
    'CDLBREAKAWAY','CDLCLOSINGMARUBOZU','CDLCONCEALBABYSWALL','CDLCOUNTERATTACK','CDLDARKCLOUDCOVER',\
    'CDLDOJI','CDLDOJISTAR','CDLDRAGONFLYDOJI','CDLENGULFING','CDLEVENINGDOJISTAR',\
    'CDLEVENINGSTAR','CDLGAPSIDESIDEWHITE','CDLGRAVESTONEDOJI','CDLHAMMER','CDLHANGINGMAN',\
    'CDLHARAMI','CDLHARAMICROSS','CDLHIGHWAVE','CDLHIKKAKE','CDLHIKKAKEMOD',\
    'CDLHOMINGPIGEON','CDLIDENTICAL3CROWS','CDLINNECK','CDLINVERTEDHAMMER','CDLKICKING',\
    'CDLKICKINGBYLENGTH','CDLLADDERBOTTOM','CDLLONGLEGGEDDOJI','CDLLONGLINE','CDLMARUBOZU',\
    'CDLMATCHINGLOW','CDLMATHOLD','CDLMORNINGDOJISTAR','CDLMORNINGSTAR','CDLONNECK',\
    'CDLPIERCING','CDLRICKSHAWMAN','CDLRISEFALL3METHODS','CDLSEPARATINGLINES','CDLSHOOTINGSTAR',\
    'CDLSHORTLINE','CDLSPINNINGTOP','CDLSTALLEDPATTERN','CDLSTICKSANDWICH','CDLTAKURI',\
    'CDLTASUKIGAP','CDLTHRUSTING','CDLTRISTAR','CDLUNIQUE3RIVER','CDLUPSIDEGAP2CROWS',\
    'CDLXSIDEGAP3METHODS')

# K线组合形态中有趋势组合和反转组合，需要加以甄别。
CANDLESTICK_PATTERN_NOTE = ('reverse','trend','trend','reverse','trend',\
    'reverse','trend','reverse','reverse','reverse',\
    'reverse','alone','reverse','trend','trend',\
    'alone','reverse','reverse','trend','reverse',\
    'reverse','trend','reverse','reverse','reverse',\
    'reverse','reverse','reverse','trend','trend',\
    'reverse','trend','trend','reverse','trend',\
    'trend','reverse','alone','alone','reverse',\
    'reverse','trend','reverse','reverse','trend',\
    'reverse','alone','trend','trend','trend',\
    'alone','alone','reverse','trend','alone',\
    'trend','trend','reverse','reverse','reverse',\
    'trend')

# 展示蜡烛图组合模式的默认尺度
DEFAULT_SCALE_CANDLESTICK_PATTERN = 1

# K线组合形态的样本数量
LITTLE_SCALE_CANDLESTICK_PATTERN_MATCH_CNT = (0,) # 微尺度时间周期的蜡烛图组合模式样板数目
SMALL_SCALE_CANDLESTICK_PATTERN_MATCH_CNT = (100,) # 小尺度时间周期
MEDIUM_SCALE_CANDLESTICK_PATTERN_MATCH_CNT = (100,) # 中尺度时间周期
BIG_SCALE_CANDLESTICK_PATTERN_MATCH_CNT = (100,) # 大尺度时间周期
CANDLESTICK_PATTERN_MATCH_CNT = (LITTLE_SCALE_CANDLESTICK_PATTERN_MATCH_CNT*2 + \
                           SMALL_SCALE_CANDLESTICK_PATTERN_MATCH_CNT*2 + \
                          MEDIUM_SCALE_CANDLESTICK_PATTERN_MATCH_CNT*4 + \
                          BIG_SCALE_CANDLESTICK_PATTERN_MATCH_CNT*3)

CANDLESTICK_PATTERN_MATCH_STOCK_GAP = 7900#100天=400小时(4小时/天)
#400*12(5min)+400*4(15min)+400*2(30min)+400*1(1hour)+200(2hour)+100(4hour)

CANDLESTICK_PATTERN_MATCH_FUTURE_GAP = 48100#100天=2400小时（24小时/天）
#2400*12(5min)+2400*4(15min)+2400*2(30min)+2400(1hour)+1200(2hour)+600(4hour)+400(6hour)+200(12hour)+100

# 移动平均线 -- 依据"招商银行黄金行情"软件的均线进行设置(周/月/季度/半年/年线)
MOVING_AVERAGE_LINE = (5,22,66,135,270)
# 布林线 -- 参数默认设为20
BOLLINGER_BANDS = 20
#=================================================================================
# 行情数据库中记录项
QUOTATION_STRUCTURE = ('time','open','high','low','close')
#循环定时器周期
# 行情数据库记录项周期: 6sec(不生成db文件),5min,15min,30min,1hour,2hour,4hour,6hour,12hour,1day,1week
QUOTATION_DB_PREFIX = ('6sec','5min','15min','30min','1hour','2hour','4hour','6hour','12hour','1day','1week')
QUOTATION_DB_PERIOD = (6,5*60,15*60,30*60,1*3600,2*3600,4*3600,6*3600,12*3600,24*3600,5*24*3600)
# 日线和周线定时器周期时间调整（日线需减去每日的结算时间，周线需减去周六闭市时间差） 2017-11-02

# 期货/大宗商品/股票的周期行情数据更新基准定时器是5min，亦是其盈亏策略数据更新定时器。
UPDATE_BASE_PERIOD = 5*60

# 策略盈亏率数据库文件对应的DataFrame结构。‘id’，‘tmChainIndx’和‘restCnt’是区别于SER数据库特有的字段。
SER_DF_STRUCTURE = ('time','price','period','patternName','patternVal','DeadTime',\
    'M15maxEarn', 'M15maxEarnTime', 'M15maxLoss', 'M15maxLossTime',\
    'M30maxEarn', 'M30maxEarnTime', 'M30maxLoss', 'M30maxLossTime',\
    'H1maxEarn', 'H1maxEarnTime', 'H1maxLoss', 'H1maxLossTime',\
    'H2maxEarn', 'H2maxEarnTime', 'H2maxLoss', 'H2maxLossTime',\
    'H4maxEarn', 'H4maxEarnTime', 'H4maxLoss', 'H4maxLossTime',\
    'H6maxEarn', 'H6maxEarnTime', 'H6maxLoss', 'H6maxLossTime',\
    'H12maxEarn', 'H12maxEarnTime', 'H12maxLoss', 'H12maxLossTime','tmChainIndx','restCnt')
SER_MAX_PERIOD = (len(QUOTATION_DB_PERIOD)-2)#去掉HB定时器周期和SER刷新周期

#链式计数:5min/15min/30min/1hour/2hour/4hour/6hour/12hour/1day/1week
CHAIN_PERIOD = (5*60,15*60-5*60,30*60-15*60,1*3600-30*60,2*3600-1*3600,4*3600-2*3600,6*3600-4*3600,\
                12*3600-6*3600,24*3600-12*3600,24*5*3600-24*3600)

TIME_SEGMENT_DICT ={"Gold_saint":["14:00:00","18:59:59"],\
                    "Silver_saint":["19:00:00","23:59:59"],\
                    "Copper_saint":["00:00:00","13:59:59"]}
#=====================================================================================
# 夏令时(Daylight saving time)和冬令时(standard time)
# 夏令时定义(欧盟国家)：3月最后一个星期日开始，10月最后一个星期日结束。
# time类中"tm_isdst"貌似有点水土不服！
# 夏令时每日结算时间:5点到6点(6点整开盘)
DAYLIGHT_SETTLEMENT_HOUR_TIME=5
SAT_DAYLIGHT_SETTLEMENT_HOUR_TIME=3
# 冬令时每日结算时间:6点到7点(7点整开盘)
STANDARD_SETTLEMENT_HOUR_TIME=6
SAT_STANDARD_SETTLEMENT_HOUR_TIME=3

def get_last_sunday_of_month(year,month):
    """ 内部接口API:获取当月(March and October)的最后一个周日对应日期
    """
    #当月1号对应星期几
    firstDayWeek = int(datetime.datetime(year, month, 1).strftime("%w"))
    #最后一个周日的日期（该规律仅限March and October等大月份）
    if firstDayWeek < 5:
        return 29 - firstDayWeek
    else:
        return 36 - firstDayWeek

def is_futures_closed():
    """ 外部接口API:判断当前时间是否为闭市时间 """
    # 每工作日凌晨5点到6点为结算时间
    now = datetime.datetime.now()
    year,month,day,hour = int(now.strftime("%Y")),int(now.strftime("%m")),int(now.strftime("%d")),int(now.strftime("%H"))
    weekday = int(now.isoweekday())
    if month >= 3 and month <= 10:#夏令时每日结算时间
        if (month == 3 and day < get_last_sunday_of_month(year,month)) or \
            (month == 10 and day > get_last_sunday_of_month(year,month)):#冬令时段的边缘日期
            if hour == STANDARD_SETTLEMENT_HOUR_TIME:
                return True
        else:
            if hour == DAYLIGHT_SETTLEMENT_HOUR_TIME:
                return True
    else:#冬令时每日结算时间
        if hour == STANDARD_SETTLEMENT_HOUR_TIME:
            return True

    # 对于欧美节假日休市的处理
    for dictHolidayItem in HOLIDAY_DATE:
        if dictHolidayItem['month']==month and dictHolidayItem['day']==day:
            return True
    return False

def be_exited(target):
    """ 外部接口API:是否退出程序。 """
    now = datetime.datetime.now()
    day, hour, minute = now.isoweekday(),now.strftime("%H"),now.strftime("%M")
    if re.search(r'[^a-zA-Z]',target) is None:#大宗商品类型全是英文字母
        if int(day) >= 6 and int(hour) > SAT_STANDARD_SETTLEMENT_HOUR_TIME:
            return True
    elif re.search(r'[^0-9](.*)',target) is None:#股票类型全是数字
        if int(hour) >= 15 and int(minute) >= 30:
            return True
    return False

# 欧美国家节假日的定义
NEW_YEAR_DAY = {'month':1,'day':1}
MARTIN_LUTHER_KING_DAY = {'month':1,'day':15}
CRUCIFIXION_JESUS_DAY = {'month':3,'day':30}
INDEPENDENCE_DAY = {'month':7,'day':4}
CHRISTMAS = {'month':12,'day':25}
HOLIDAY_DATE = (NEW_YEAR_DAY,MARTIN_LUTHER_KING_DAY,CRUCIFIXION_JESUS_DAY,INDEPENDENCE_DAY,CHRISTMAS)

# KLine--组合模式；MA--趋势；MACD--金叉/死叉；BBand--压力/支撑位
ABSTRACT_TITLE = {'KLine':'\nKLine Give suggestion with direction:',\
                  'MA':'\nMA Give trends:',\
                  'MACD':'\nMACD Give suggestion with:',\
                  'BBand':'\nBBand is at position with:'}

#==============================================================================================
def is_stock_closed():
    """ 外部接口API:判断当前时间是否为休市时间
        返回值：True---休/闭市时间；False---交易时间
    """
    now = datetime.datetime.now()
    year,month,day = now.strftime("%Y"),now.strftime("%m"),now.strftime("%d")
    weekday = int(now.isoweekday())
    if weekday > 5:
        return True

    # 判断是否特定节假日
    holiday = Configuration.get_property('holiday')
    if holiday is not None:
        for date in holiday.split(';'):
            if date == '%s-%s-%s'%(year,month,day):
                return True

    realnumNow = time.mktime(now.timetuple())
    EXCHANGE_AM_START = datetime.datetime.strptime(year+'-'+month+'-'+day+' 09:25:00',"%Y-%m-%d %H:%M:%S")
    realnumAMStart = time.mktime(EXCHANGE_AM_START.timetuple())
    EXCHANGE_AM_END = datetime.datetime.strptime(year+'-'+month+'-'+day+' 11:30:59',"%Y-%m-%d %H:%M:%S")
    realnumAMEnd = time.mktime(EXCHANGE_AM_END.timetuple())
    EXCHANGE_PM_START = datetime.datetime.strptime(year+'-'+month+'-'+day+' 13:00:00',"%Y-%m-%d %H:%M:%S")
    realnumPMStart = time.mktime(EXCHANGE_PM_START.timetuple())
    # 截止时间延后，确保高阶定时器计数能够完成每日的最后一次刷新
    EXCHANGE_PM_END = datetime.datetime.strptime(year+'-'+month+'-'+day+' 15:15:59',"%Y-%m-%d %H:%M:%S")
    realnumPMEnd = time.mktime(EXCHANGE_PM_END.timetuple())

    if realnumAMStart <= realnumNow and realnumNow <= realnumAMEnd:#上午交易时段
        return False
    elif realnumPMStart <= realnumNow and realnumNow <= realnumPMEnd:#下午交易时段
        return False
    else:
        return True

def is_closed(target):
    """ 外部接口API:判断当前时间是否为休市时间
        返回值：True---休/闭市时间；False---交易时间
    """
    if re.search(r'[^a-zA-Z]',target) is None:#大宗商品类型全是英文字母
        if is_futures_closed():
            return True
    elif re.search(r'[^0-9](.*)',target) is None:#股票类型全是数字
        if is_stock_closed():
            return True
    return False
