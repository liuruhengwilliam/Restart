#coding=utf-8

# 行情数据库操作原语
QUOTATION_DB_CREATE = 'create table quotation(\
    id integer primary key autoincrement not null default 1,\
    startPrice float, realPrice float, maxPrice float, minPrice float, time float);'

QUOTATION_DB_INSERT = 'insert into quotation (startPrice,realPrice,maxPrice,minPrice,time)\
    values(?, ?, ?, ?, ?)'
