#coding=utf-8

from resource import Constant
import threading
from Coordinate import *
from timer import TimerMotor
from resource import Constant
import platform

Configuration.create_working_directory() #创建当周工作目录
Configuration.create_period_working_folder() #创建各周期属性文件夹
Constant.envi_init()#初始化杂项

def server_main():
    """执行模块"""
    # 数据抓取和行情数据库相关初始化
    coordinate = Coordinate()

    coordinate.init_module()

    # 数据抓取模块和数据库模块挂载到周期定时器
    HBfuncHook = (coordinate.work_heartbeat,) # 心跳定时器处理回调函数
    PeriodfuncHook = (coordinate.work_server_operation,) # 一般周期定时器处理回调函数
    funcList = (HBfuncHook + PeriodfuncHook*8) # 回调函数列表

    # 周期定时器线程启动
    TimerMotor.start_loop_timer(funcList,Constant.QUOTATION_DB_PERIOD)

def client_main():
    coordinate = Coordinate()
    TimerMotor.start_loop_timer((coordinate.work_client_operation,),(Constant.QUOTATION_DB_PERIOD[1],))

if __name__ == '__main__':
    if (platform.system() == "Linux"):#服务器端主线程
        server_main()
    else:#客户端主线程
        client_main()
