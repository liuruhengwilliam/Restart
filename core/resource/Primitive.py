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
# 建表
EARNRATE_DB_CREATE = 'create table earnrate(\
    id integer primary key autoincrement not null default 1,\
    direction int, price float,time float,\
    5minDetermine int, 15minDetermine int, 30minDetermine int, 1hourDetermine int, 2hourDetermine int,\
    4hourDetermine int, 6hourDetermine int, 12hourDetermine int, 1dayDetermine int, 1weekDetermine int,\
    maxEarn float, maxEarnTime float, minEarn float,minEarnTime float,\
    5minEarn float, 15minEarn float, 30minEarn float, 1hourEarn float, 2hourEarn float,\
    4hourEarn float, 6hourEarn float, 12hourEarn float, 1dayEarn float, 1weekEarn float);'

# 插入
EARNRATE_DB_INSERT = 'insert into earnrate(direction,price,time,5minDetermine,15minDetermine,\
    30minDetermine,1hourDetermine,2hourDetermine,4hourDetermine,6hourDetermine,12hourDetermine,\
    1dayDetermine,1weekDetermine) values(?,?,?,?,?,?,?,?,?,?,?,?,?)'

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