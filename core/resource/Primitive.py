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
# 策略盈亏率数据库操作原语
# 建表
# 表结构说明：
#策略点时间，策略点价格，策略点方向，周期名称，技术指标名称（组合图形名称索引或其他）
#策略点给出后盈亏率时间统计:（极值及时间/5min/15min/30min/1hour/2hour/4hour/6hour/12hour/1day/1week）
STRATEARNRATE_DB_CREATE = 'create table stratearnrate(\
    indx integer primary key autoincrement not null default 1,\
    time text, price float, tmName text, patternName text,patternVal int, \
    maxEarn float, maxEarnTime text, minEarn float,minEarnTime text,\
    M5Earn float, M15Earn float, M30Earn float, H1Earn float, H2Earn float,\
    H4Earn float, H6Earn float, H12Earn float, D1Earn float, W1Earn float);'

# 插入: 时间，价格，方向，周期名称，匹配模式名称
STRATEARNRATE_DB_INSERT=\
    'insert into stratearnrate(time,price,tmName,patternName,patternVal,\
    maxEarn,maxEarnTime,minEarn,minEarnTime,M5Earn,M15Earn,M30Earn,\
    H1Earn,H2Earn,H4Earn,H6Earn,H12Earn,D1Earn,W1Earn) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

def query_stratearnrate_db(indxValue):
    """ 外部接口API：根据数据库条目id查找相应记录项
        indxValue: 条目序号值
    """
    "select * from stratearnrate where indx = '%s'" % indxValue

def update_stratearnrate_db(id,column,value):
    """ 外部接口API：根据数据库条目id更新相应记录项
        id: 条目id
        column: 条目id具体某项
        value: column对应的值
    """
    "update stratearnrate set %s = %s where id = %s"% column, value, id