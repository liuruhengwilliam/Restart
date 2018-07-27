#coding=utf-8

import os
import Queue
from timer import TimerMotor
from Coordinate import *
from resource import Constant
from resource import Trace
from resource import Configuration

Configuration.create_working_directory() #创建工作目录
Constant.envi_init()#初始化杂项
def stock_main():
    """ 股票行情模块主函数 """
    # 相关队列
    inter2exterQueue = Queue.Queue()

    #也可使用配置文件设置循环定时器的方式
    period = Configuration.get_property("stockCatchPeriod")#单位是秒
    if period == None:
        period = Constant.QUOTATION_DB_PERIOD[0]

    # 数据抓取和行情数据库相关初始化
    coordinate = Coordinate(inter2exterQueue)

    # 数据抓取模块和数据库模块挂载到周期定时器
    HBfuncHook = (coordinate.work_heartbeat_query,) # 心跳定时器处理回调函数
    # 操作处理回调函数。出于减少定时器操作复杂度的考虑，只保留一个5min级别的定时器。其他周期就在5min基础上收集整理信息。
    PeriodfuncHook = (coordinate.work_internal_operate,coordinate.work_external_operate)#增加存档线程20180607
    funcList = (HBfuncHook + PeriodfuncHook) # 回调函数列表

    TimerMotor.start_loop_timer(funcList,[int(period),Constant.UPDATE_BASE_PERIOD,Constant.REFRESH_PERIOD])

if __name__ == '__main__':
    stock_main()
