#coding=utf-8

# 行情数据库操作原语
QUOTATION_DB_CREATE = 'create table quotation(\
    id integer primary key autoincrement not null default 1,\
    open float, high float, low float, close float, time float);'

# 插入操作
QUOTATION_DB_INSERT = 'insert into quotation (open,high,low,close,time)\
    values(?, ?, ?, ?, ?)'

# id升序排列的查询操作 2017-10-31
QUOTATION_DB_QUERY_ASC = 'select * from quotation'

# id降序排列的查询原语 2017-11-13
QUOTATION_DB_QUERY_DESC = 'select * from quotation order by id desc'

#=================================================================================
# 盈利数据库操作原语
EARNRATE_DB_CREATE = 'create table earnrate(\
    id integer primary key autoincrement not null default 1,\
    direction int, time float,\
    5minDetermine int, 15minDetermine int, 30minDetermine int, 1hourDetermine int, 2hourDetermine int,\
    4hourDetermine int, 6hourDetermine int, 12hourDetermine int, 1dayDetermine int, 1weekDetermine int,\
    maxEarn float, maxEarnTime float, minEarn float,minEarnTime float,\
    30minEarn float, 1hourEarn float, 2hourEarn float, 4hourEarn float, 6hourEarn float, 12hourEarn float,\
    1dayEarn float, 1weekEarn float);'