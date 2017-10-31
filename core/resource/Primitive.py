#coding=utf-8

# 行情数据库操作原语
QUOTATION_DB_CREATE = 'create table quotation(\
    id integer primary key autoincrement not null default 1,\
    startPrice float, realPrice float, maxPrice float, minPrice float, time float);'

# 插入操作
QUOTATION_DB_INSERT = 'insert into quotation (startPrice,realPrice,maxPrice,minPrice,time)\
    values(?, ?, ?, ?, ?)'

# 查询操作 2017-10-31
QUOTATION_DB_QUERY = 'select * from quotation'
# 区间查询原语
#QUOTATION_DB_QUERY = 'select * from quotation limit 0,10'