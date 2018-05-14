#coding=utf-8

import os
import platform
import Configuration

DEBUG_LEVEL = ('fatal','warn','info','debug')

def output(requestLevel, content):
    """ 外部接口API：调试输出及日志信息
        入参：requestLevel---调试日志的输出等级
             content---调试日志具体内容
    """
    default_level = len(DEBUG_LEVEL) # 默认全部输出
    # 若输出等级字符不识别，则直接返回。
    if DEBUG_LEVEL.count(requestLevel) == 0:
        return
    # ==== ==== ==== ==== 总开关 ==== ==== ==== ====
    ret = Configuration.get_property("trace")
    if ret == 'False' :
        return

    # ==== ==== ==== ==== 控制台输出功能 ==== ==== ==== ====
    # 从XML配置文件中获取控制台输出开关
    ret = Configuration.get_property("consoletrace")
    if ret == 'True' :
        print content

    # ==== ==== ==== ==== 日志功能 ==== ==== ==== ====
    # 从XML配置文件中获取调试日志的输出等级
    ret = Configuration.get_property("loglevel")
    if ret is not None:
        default_level = DEBUG_LEVEL.index(ret)

    # 若输出等级低于门槛等级，则直接返回。
    if default_level < DEBUG_LEVEL.index(requestLevel):
        return

    traceFile = Configuration.get_working_directory()+'trace.txt'
    if not os.path.exists(traceFile):
        fileHandle = open(traceFile,'w') #创建文件
    else:
        fileHandle = open(traceFile,'a') #追加方式

    if type(content) is list:
        fileHandle.write('\n' + ' '.join(content))
    else:
        fileHandle.write('\n' + content)
    fileHandle.close()
