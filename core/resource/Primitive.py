#coding=utf-8

# 行情数据库操作原语
QUOTATION_DB_CREATE = 'create table quotation(\
    id integer primary key autoincrement not null default 1,\
    time float, open float, high float, low float, close float);'

# 插入操作
QUOTATION_DB_INSERT = 'insert into quotation (time,open,high,low,close)\
    values(?, ?, ?, ?, ?)'

# id升序排列的查询操作 2017-10-31
QUOTATION_DB_QUERY_ASC = 'select * from quotation'

# id降序排列的查询原语 2017-11-13
QUOTATION_DB_QUERY_DESC = 'select * from quotation order by id desc'

#=================================================================================
# 盈利数据库操作原语
# 建表
EARNRATE_DB_CREATE = 'create table earnrate(\
    id integer primary key autoincrement not null default 1,\
    direction int, price float,time float,\
    M5Dtrm int, M15Dtrm int, M30Dtrm int, H1Dtrm int, H2Dtrm int,\
    H4Dtrm int, H6Dtrm int, H12Dtrm int, D1Dtrm int, W1Dtrm int,\
    maxEarn float, maxEarnTime float, minEarn float,minEarnTime float,\
    M5Earn float, M15Earn float, M30Earn float, H1Earn float, H2Earn float,\
    H4Earn float, H6Earn float, H12Earn float, D1Earn float, W1Earn float);'

# 插入
EARNRATE_DB_INSERT = 'insert into earnrate(direction,price,time,M5Dtrm,M15Dtrm,M30Dtrm,H1Dtrm,\
    H2Dtrm,H4Dtrm,H6Dtrm,H12Dtrm,D1Dtrm,W1Dtrm) values(?,?,?,?,?,?,?,?,?,?,?,?,?)'

def query_earnrate_db(column,id = ''):
    """ 外部接口API：根据数据库条目id查找相应记录项
        id: 条目id
        column: 条目id具体某项
    """
    if id == '':
        "select '%s' from earnrate" % column
    else:
        "select '%s' from earnrate where id = '%s'" % column,id

def update_earnrate_db(id,column,value):
    """ 外部接口API：根据数据库条目id更新相应记录项
        id: 条目id
        column: 条目id具体某项
        value: column对应的值
    """
    "update earnrate set %s = %s where id = %s"% column, value, id