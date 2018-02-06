#coding=utf-8

import os
from resource import Constant
import threading
from Coordinate import *
from timer import TimerMotor
from resource import Constant
import platform

Configuration.create_working_directory() #创建当周工作目录
Configuration.create_period_working_folder() #创建各周期属性文件夹
Constant.envi_init()#初始化杂项
#程序运行的角色：Server 或者 Client
ROLE_DEFAULT = "Server"

def server_main():
    """执行模块"""
    # 数据抓取和行情数据库相关初始化
    coordinate = Coordinate('Server')

    # 数据抓取模块和数据库模块挂载到周期定时器
    HBfuncHook = (coordinate.work_heartbeat,) # 心跳定时器处理回调函数
    PeriodfuncHook = (coordinate.work_server_operation,) # 一般周期定时器处理回调函数
    funcList = (HBfuncHook + PeriodfuncHook*8) # 回调函数列表

    # 周期定时器线程启动
    TimerMotor.start_loop_timer(funcList,Constant.QUOTATION_DB_PERIOD)

def client_main():
    coordinate = Coordinate('Client')
    coordinate.work_client_operation()#客户端启动时就运行
    #在Linux平台下可以利用while命令循环执行shell命令
    #参考文档：http://blog.csdn.net/daoshuti/article/details/72831256

    #也可使用配置文件设置循环定时器的方式
    clientPeriod = Configuration.get_property("clientPeriod")#单位是秒
    if clientPeriod == None:
        clientPeriod = Constant.QUOTATION_DB_PERIOD[1]
    TimerMotor.start_loop_timer((coordinate.work_client_operation,),[int(clientPeriod),])

if __name__ == '__main__':
    ROLE_DEFAULT = Configuration.get_property("programrole")
    if ROLE_DEFAULT == "Server":#服务器端主线程
        server_main()
    elif ROLE_DEFAULT == "Client":#客户端主线程
        client_main()
    else:#如果没有设置就强制退出
        os._exit(0)
