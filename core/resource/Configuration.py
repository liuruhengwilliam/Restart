#coding=utf-8

import os
import datetime
import platform
import threading
import Trace

import xml.etree.ElementTree as ET

def get_working_directory():
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
        dirPath = os.getcwd()+'\\'+fileNamePrefix+'\\'
    elif (sysName == "Linux"):
        dirPath = os.getcwd()+'/'+fileNamePrefix+'/'
    else :# 未知操作系统
        dirPath = fileNamePrefix

    if not os.path.exists(dirPath):
        # 创建当周数据库文件夹
        os.makedirs(dirPath)

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
