#coding=utf-8

import os
from resource import Constant
from Coordinate import *
from timer import TimerMotor

Configuration.create_working_directory() #创建当周工作目录
Constant.envi_init()#初始化杂项

def server_main():
    """执行模块"""
    # 数据抓取和行情数据库相关初始化
    coordinate = Coordinate()

    # 数据抓取模块和数据库模块挂载到周期定时器
    HBfuncHook = (coordinate.work_heartbeat,) # 心跳定时器处理回调函数
    PeriodfuncHook = (coordinate.work_operation,) # 一般周期定时器处理回调函数
    funcList = (HBfuncHook + PeriodfuncHook) # 回调函数列表

    # 周期定时器线程启动
    TimerMotor.start_loop_timer(funcList,Constant.QUOTATION_DB_PERIOD)

if __name__ == '__main__':
    server_main()
