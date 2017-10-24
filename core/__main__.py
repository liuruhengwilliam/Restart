#coding=utf-8

import threading
from database import QuotationDB
from engine import DataScrape
from coordinateDS2QDB import *
from timer.TimerMotor import TimerMotor
from resource import Configuration

def main():
    """执行模块"""
    # 数据抓取和行情数据库相关初始化
    core4DS = coordinateDS2QDB()
    core4DS.init_data_scrape()
    core4DS.init_quotation_db()

    funcList = [] # 回调函数列表
    # 数据抓取模块和行情数据库模块挂载到周期定时器
    funcList.append(core4DS.work_DS2QDB_heartbeat)
    funcList.extend([core4DS.work_DS2QDB_operate]*10)

    timerMotorHdl = TimerMotor()
    # 初始化固定周期定时器
    timerMotorHdl.init_fasten_timer(funcList, Configuration.QUOTATION_DB_PERIOD)

    #ER数据库
    #......

    # 定时器线程启动
    timerMotorHdl.start_timer()

if __name__ == '__main__':
    main()