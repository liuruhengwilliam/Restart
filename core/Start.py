#coding=utf-8

from resource import Constant
Constant.envi_init()#初始化杂项

import threading
from Coordinate import *
from timer import TimerMotor
from resource import Constant

def main():
    """执行模块"""
    # 数据抓取和行情数据库相关初始化
    coordinate = Coordinate()

    coordinate.init_quotation()

    funcList = [] # 回调函数列表
    # 数据抓取模块和行情数据库模块挂载到周期定时器
    funcList.append(coordinate.work_heartbeat)
    funcList.extend([coordinate.work_operation]*10)

    # 周期定时器线程启动
    TimerMotor.start_loop_timer(funcList,Constant.QUOTATION_DB_PERIOD)

if __name__ == '__main__':
    main()
