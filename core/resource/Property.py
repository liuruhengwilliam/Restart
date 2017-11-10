#coding=utf-8

import os
import datetime
import platform
import xml.etree.ElementTree as ET
import Configuration

# 对于程序运行过程中的调试和异常等情况，需要通过XML配置文件加载相关属性方式调整流程，便于分析问题。

def get_property(strProperty):
    """ 内部接口API：根据XML配置文件读取相关属性字段
        入参：strProperty 属性字符串
        返回值：若XML文件中存在对应属性，则返回属性值；否则返回None。
    """
    ret = None
    fileName = Configuration.get_working_directory()+'/Properties.xml'

    if not os.path.exists(fileName):
        return

    try:
        tree = ET.parse(fileName)
        root = tree.getroot()
    except Exception,e:
        print e.message
        return

    for item in root.findall(strProperty):
        ret = item.find('value').text

    return ret