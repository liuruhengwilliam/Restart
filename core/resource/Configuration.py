#coding=utf-8

import os
import urllib
import datetime
import platform
import threading
import Trace
import Constant

import xml.etree.ElementTree as ET

def create_working_directory():
    """ 内/外部接口API：获取当前周工作目录
        返回值:工作目录字符串
    """
    # 寻找当前周数并生成文件名前缀
    dt = datetime.datetime.now()
    year,week = dt.strftime('%Y'),dt.strftime('%U')
    fileNamePrefix = year+'-'+week

    #生成文件路径(依据不同操作系统)
    sysName = platform.system()
    if (sysName == "Windows"):
        dirPath = os.getcwd()+'\\'+year+'\\'+fileNamePrefix+'\\'
    elif (sysName == "Linux"):
        dirPath = os.getcwd()+'/'+year+'/'+fileNamePrefix+'/'
    else :# 未知操作系统
        dirPath = fileNamePrefix

    if not os.path.exists(dirPath):
        # 创建当周数据库文件夹
        os.makedirs(dirPath)

def get_working_directory():
    """内/外部接口API：获取当前周工作目录"""
    dt = datetime.datetime.now()
    year,week = dt.strftime('%Y'),dt.strftime('%U')
    fileNamePrefix = year+'-'+week

    #生成文件路径(依据不同操作系统)
    sysName = platform.system()
    if (sysName == "Windows"):
        dirPath = os.getcwd()+'\\'+year+'\\'+fileNamePrefix+'\\'
    elif (sysName == "Linux"):
        dirPath = os.getcwd()+'/'+year+'/'+fileNamePrefix+'/'
    else :# 未知操作系统
        dirPath = fileNamePrefix

    return dirPath

def get_backweek_period_directory(backDeepCnt,periodName):
    """ 外部接口API：获取前若干周某周期下的目录
        backDeepCnt: 追溯的历史周数
        periodName: 当前周名称的字符串
    """
    someday = datetime.date.today() - datetime.timedelta(weeks=backDeepCnt)
    year,week = someday.strftime('%Y'),someday.strftime('%U')# 获取前一周的年份和周数
    sysName = platform.system()
    if (sysName == "Windows"):
        dirPath = os.getcwd()+'\\'+year+'\\'+'%s-%s'%(year,week)+'\\'+periodName+'\\'
    elif (sysName == "Linux"):
        dirPath = os.getcwd()+'/'+year+'/'+'%s-%s'%(year,week)+'/'+periodName+'/'
    else :# 未知操作系统
        dirPath = get_working_directory()

    return dirPath

def create_period_working_folder():
    """外部接口API: 创建各周期所属文件夹。用来存放csv和png等文件"""
    for tagPeriod in Constant.QUOTATION_DB_PREFIX:
        sysName = platform.system()
        if (sysName == "Windows"):
            dirPath = get_working_directory()+tagPeriod
        elif (sysName == "Linux"):
            dirPath = get_working_directory()+tagPeriod
        else :# 未知操作系统
            dirPath = tagPeriod

        if not os.path.exists(dirPath):
            # 创建当周数据库文件夹
            os.makedirs(dirPath)

def get_period_working_folder(period):
    """ 外部接口API：获取某周期的属性文件夹路径
        period: 周期字符名称
    """
    sysName = platform.system()
    if (sysName == "Windows"):
        dirPath = get_working_directory()+period+'\\'
    elif (sysName == "Linux"):
        dirPath = get_working_directory()+period+'/'
    else :# 未知操作系统
        dirPath = period
    return dirPath

# 对于程序运行过程中的调试和异常等情况，需要通过XML配置文件加载相关属性方式调整流程，便于分析问题。
def get_property(strProperty):
    """ 内/外部接口API：根据XML配置文件读取相关属性字段
        入参：strProperty 属性字符串
        返回值：若XML文件中存在对应属性，则返回属性值；否则返回None。
    """
    ret = None
    fileName = get_working_directory()+'Properties.xml'

    if not os.path.exists(fileName):
        return None

    try:
        tree = ET.parse(fileName)
        root = tree.getroot()
    except Exception,e:
        Trace.output('fatal','get_property exception:'+e.message)
        return None

    for item in root.findall(strProperty):
        ret = item.find('value').text

    return ret

DEFAULT_SERVER_URL = "http://192.168.10.81/"
DEFAULT_PHASE_VERSION = "Fx678-V093AQ"
def get_server_download_url(period):
    """ 外部接口API：获取远端服务器(only should be Linux)的下载url
        period: 周期名称字符串
    """
    dt = datetime.datetime.now()
    year,week = dt.strftime('%Y'),dt.strftime('%U')
    fileNamePrefix = year+'-'+week

    serverUrl = get_property('serverUrl')
    if serverUrl == None:
        serverUrl = DEFAULT_SERVER_URL

    phaseVersion = get_property('phaseVer')
    if phaseVersion == None:
        phraseVersion = DEFAULT_PHASE_VERSION

    return serverUrl + phaseVersion + '/'+year+'/'+fileNamePrefix+'/'+period+'/'

def download_realtime_file(suffix):
    """ 外部接口API:下载实时更新的文件--相关数据库文件
        suffix:文件名伪后缀-- ser or quote
    """
    for tmName in Constant.QUOTATION_DB_PREFIX[1:]:
        dnldUrl = get_server_download_url(tmName)+tmName+'-'+suffix+'.db'
        filePath = get_period_working_folder(tmName)+tmName+'-'+suffix+'-dup.db'
        try:
            urllib.urlretrieve(dnldUrl,filename=filePath)
            Trace.output('info',"download db file from %s"%(dnldUrl))
        except Exception,e:
            continue

def download_statistic_file(suffix):
    """外部接口API：下载每日结算期统计文件--相关csv和png文件
        suffix:文件后缀-- csv or png
    """
    for tmName in Constant.QUOTATION_DB_PREFIX[1:]:
        if suffix == "csv":#制表文件
            for phase in ("quote","ser"):
                dnldUrl = get_server_download_url(tmName)+\
                        tmName+'-'+phase+str(datetime.date.today())+'.'+suffix
                filePath = get_period_working_folder(tmName)+\
                        tmName+'-'+phase+str(datetime.date.today())+'.'+suffix
                try:
                    urllib.urlretrieve(dnldUrl,filename=filePath)
                    Trace.output('info',"download db file from %s"%(dnldUrl))
                except Exception,e:
                    continue
        else:#png文件
            #下载前一天的指标绘图文件
            dayStamp = (datetime.date.today()-datetime.timedelta(days=1)).strftime('%b%d')
            for clock in range(24):
                dnldUrl = get_server_download_url(tmName)+\
                        tmName+'-'+dayStamp+'_'+'%02d'%clock+'_00'+'.'+suffix
                filePath = get_period_working_folder(tmName)+\
                        tmName+'-'+dayStamp+'_'+'%02d'%clock+'_00'+'.'+suffix
                try:
                    urllib.urlretrieve(dnldUrl,filename=filePath)
                    Trace.output('info',"download db file from %s"%(dnldUrl))
                except Exception,e:
                    continue

def exit_client():
    """外部接口API：客户端程序退出检测
        配置文件可设置。若未设定则默认退出。
    """
    exitClient = True
    exitClient = get_property('exitClient')
    return exitClient