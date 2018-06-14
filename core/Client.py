#coding=utf-8
import os
from timer import TimerMotor
from resource import Constant
from resource import Trace
from resource import Configuration
from statistics.Statistics import Statistics

Configuration.create_working_directory() #创建工作目录

def client_main():
    # 依赖目录可能有若干个
    pathTotal = Configuration.get_property("dependDataPath")
    if pathTotal == None:
        Trace.output('fatal','no data path depended!')
        return

    #也可使用配置文件设置循环定时器的方式
    clientPeriod = Configuration.get_property("clientPeriod")#单位是秒
    if clientPeriod == None:
        clientPeriod = Constant.QUOTATION_DB_PERIOD[1]

    #在Linux平台下可以利用while命令循环执行shell命令
    #参考文档：http://blog.csdn.net/daoshuti/article/details/72831256
    for path in pathTotal.split(';'):
        statisticHdl = Statistics(path)
        TimerMotor.start_loop_timer((statisticHdl.statistics_operation,),[int(clientPeriod),])

if __name__ == '__main__':
    client_main()
