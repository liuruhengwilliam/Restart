#coding=utf-8

# 行情数据库中记录项
QUOTATION_STRUCTURE = ['startPrice','realPrice','maxPrice','minPrice','time']

#循环定时器周期
# 行情数据库记录项周期: 10sec(不生成db文件),5min,15min,30min,1hour,2hour,4hour,6hour,12hour,1day,1week
QUOTATION_DB_PREFIX = ['10sec','5min','15min','30min','1hour','2hour','4hour','6hour','12hour','1day','1week']
QUOTATION_DB_PERIOD = [10,5*60,15*60,30*60,1*3600,2*3600,4*3600,6*3600,12*3600,1*24*3600,5*24*3600]

#链式定时器周期
CHAIN_PERIOD = [1800,1*3600-1800,2*3600-1*3600,4*3600-2*3600,6*3600-4*3600,\
                12*3600-6*3600,24*3600-12*3600,24*5*3600-24*3600]



