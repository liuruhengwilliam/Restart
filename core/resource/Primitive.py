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
# 表结构说明：
# 策略点方向，策略点价格，策略点时间，技术指标名称（组合图形名称索引）
# 策略点各周期决策值：（5min or 15min or 30min or 1hour or 2hour or 4hour or 6hour or 12hour or 1day or 1week）
# 策略点后盈亏值的时间统计:（最大值及时间/最小值及时间/5min/15min/30min/1hour/2hour/4hour/6hour/12hour/1day/1week）
EARNRATE_DB_CREATE = 'create table earnrate(\
    id integer primary key autoincrement not null default 1,\
    direction int, price float,time float, Dtrm int, patternName text,\
    maxEarn float, maxEarnTime float, minEarn float,minEarnTime float,\
    M5Earn float, M15Earn float, M30Earn float, H1Earn float, H2Earn float,\
    H4Earn float, H6Earn float, H12Earn float, D1Earn float, W1Earn float);'

# 插入
EARNRATE_DB_INSERT = 'insert into earnrate(direction,price,time,patternName,Dtrm) values(?,?,?,?,?)'

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