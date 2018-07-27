#coding=utf-8

import os
import Queue
from resource import Constant
from Coordinate import *
from timer import TimerMotor

Configuration.create_working_directory() #创建当周工作目录
Constant.envi_init()#初始化杂项

def server_main():
    """执行模块"""
    # 相关队列
    inter2exterQueue = Queue.Queue()

    # 数据抓取和行情数据库相关初始化
    coordinate = Coordinate(inter2exterQueue)

    # 数据抓取模块和数据库模块挂载到周期定时器
    HBfuncHook = (coordinate.work_heartbeat_query,) #心跳定时器处理回调函数
    PeriodfuncHook = (coordinate.work_internal_operate,coordinate.work_external_operate)
    funcList = (HBfuncHook + PeriodfuncHook) # 回调函数列表

    # 周期定时器线程启动
    TimerMotor.start_loop_timer(funcList,Constant.QUOTATION_DB_PERIOD[0:2]+tuple([Constant.REFRESH_PERIOD]))

if __name__ == '__main__':
    server_main()
