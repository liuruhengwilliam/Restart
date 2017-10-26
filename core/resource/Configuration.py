#coding=utf-8

import os
import datetime
import platform

# 行情数据库中记录项
QUOTATION_STRUCTURE = ('startPrice','realPrice','maxPrice','minPrice','time')

#循环定时器周期
# 行情数据库记录项周期: 6sec(不生成db文件),5min,15min,30min,1hour,2hour,4hour,6hour,12hour,1day,1week
QUOTATION_DB_PREFIX = ('6sec','5min','15min','30min','1hour','2hour','4hour','6hour','12hour','1day','1week')
QUOTATION_DB_PERIOD = (6,5*60,15*60,30*60,1*3600,2*3600,4*3600,6*3600,12*3600,1*24*3600,5*24*3600)

#链式定时器周期
CHAIN_PERIOD = (1800,1*3600-1800,2*3600-1*3600,4*3600-2*3600,6*3600-4*3600,\
                12*3600-6*3600,24*3600-12*3600,24*5*3600-24*3600)

class Configuration():
    """ 相关全局配置类 """
    def __init__(self):
        """ 初始化 """
        self.dbPath = None

    def create_db_path(self):
        """ 外部接口API: 生成数据库文件路径 """
        # 寻找当前周数并生成文件名前缀
        dt = datetime.datetime.now()
        year,week = dt.strftime('%Y'),dt.strftime('%U')
        fileNamePrefix = year+'-'+week

        #生成文件路径(依据不同操作系统)
        sysName = platform.system()
        if (sysName == "Windows"):
            self.dbPath = 'D:/misc/future/'+fileNamePrefix
        elif (sysName == "Linux"):
            self.dbPath = '~/mess/future/'+fileNamePrefix
        else :# 未知操作系统
            self.dbPath = fileNamePrefix

        if not os.path.exists(self.dbPath):
            # 创建当周数据库文件夹
            os.makedirs(self.dbPath)

        return self.dbPath

    def get_dbfile_path(self):
        """ 外部接口API：获取数据库文件路径 """
        return self.dbPath