#coding=utf-8

import threading
from database import QuotationDB
from engine import DataScrape
from timer import TimerMotor
from coordinateDS2QDB import *

def main():
    """执行模块"""
    # 数据抓取和行情数据库相关初始化
    core4DS = coordinateDS2QDB()
    core4DS.init_data_scrape()
    core4DS.init_quotation_db()

    #数据抓取模块挂载到定时器线程
    tm = TimerMotor(core4DS.work_DS2QDB_record, core4DS.work_QDB_update, core4DS.idiot)
    #定时器线程启动
    tm.start_timer()

if __name__ == '__main__':
    main()