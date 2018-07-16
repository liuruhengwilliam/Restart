#coding=utf-8
import re
import os
import csv
import sqlite3
import datetime
import numpy as np
import pandas as pd
from datetime import timedelta
from pandas import DataFrame
from matplotlib.dates import date2num
from resource import Configuration
from resource import Constant
from resource import Trace

def process_quotes_supplement(target,file):
    """ 外部接口API：补全quotes数据
        target:标的字符串
        file:行情数据记录文件(含文件路径)
        返回值: dateframe结构数据(period, time, open, high, low, close)
    """
    data = pd.read_csv(file)
    if re.search(r'[^a-zA-Z]',target) is None:#大宗商品类型全是英文字母
        gap = Constant.CANDLESTICK_PATTERN_MATCH_FUTURE_GAP
    elif re.search(r'[^0-9](.*)',target) is None:#股票类型全是数字
        gap = Constant.CANDLESTICK_PATTERN_MATCH_STOCK_GAP
    else:#异常标的不做补全处理
        return data

    if len(data) > gap:
        dataSupplement = data.iloc[-gap:]
    else:
        #dataSupplement = supplement_items(file,data,gap)
        dataSupplement = data
    # 输出日志记录
    #Trace.output('info',"=== To be continued from %s ==="%Configuration.get_field_from_string(file)[-1])
    #for itemRow in dataSupplement.itertuples(index=False):
    #    Trace.output('info','    '+(' ').join(map(lambda x:str(x), itemRow)))
    return dataSupplement

def process_ser_supplement(target,file):
    """ 外部接口API：补全ser数据
        target:标的字符串
        file:ser记录文件(含文件路径)
        返回值: dateframe结构数据
    """
    data = pd.read_csv(file)
    #筛除大于3天时间跨度的条目
    threshold = datetime.datetime.now()-timedelta(days=7)
    data.is_copy = False
    for indx,row in zip(data.index,data.itertuples()):
        if len(data.ix[indx,'time'].split(':')) == 2:
            data.ix[indx,'time'] = data.ix[indx,'time']+':00'
        if datetime.datetime.strptime(data.ix[indx,'time'],"%Y-%m-%d %H:%M:%S") < threshold:
            data.drop(indx,inplace=True)

    # 输出日志记录
    Trace.output('info',"=== To be continued from %s ==="%Configuration.get_field_from_string(file)[-1])
    for itemRow in data.itertuples(index=False):
        Trace.output('info','    '+(' ').join(map(lambda x:str(x), itemRow)))
    return data

def supplement_items(path,data,supplementCnt):
    """ 外部接口API：补齐某个数目的行情序列。
        path：路径字符串
        data: 当前周期行情dataframe结构数据
        supplementCnt: 需要增补的数目
        返回值: 增补后的dateframe结构行情数据
    """
    weekGap = 1 #从前一周开始搜索
    while supplementCnt > 0:
        prefile = Configuration.get_back_week_directory(path,weekGap)+\
                        Configuration.get_field_from_string(path)[-1]
        if not os.path.exists(prefile): #若回溯文件完毕，则退出循环。
            break

        dataSupplement = pd.read_csv(prefile)
        if dataSupplement is None or len(dataSupplement) == 0:
            supplCnt = 0
        else:
            supplCnt = len(dataSupplement)

        if supplCnt >= supplementCnt: #已经能够补全，取后面的(supplementCnt)个数据
            dataCollect = dataSupplement.iloc[supplCnt-supplementCnt:]
        elif dataSupplement is None:
            dataCollect = None
        else: #还未补全数据继续循环
            dataCollect = dataSupplement

        weekGap+=1 #时间回溯
        supplementCnt-=supplCnt #待补全的数据调整。若为负，则跳出循环。
        if dataCollect is not None:
            data = dataCollect.append(data,ignore_index=True) #按照时间顺序收集合并数据

    return data

def translate_db_into_csv(dbFile):
    """ 外部接口API:将行情数据的db文件转换成同名同路径的csv文件
        dbFile: db文件名（含文件路径）
        lineCnt: 截取db条目数目。注：‘-1’表示全部转换。
    """
    filename = '%s%s'%(dbFile.split('.')[0],'.csv')

    if not os.path.exists(dbFile) or dbFile[-8:] != 'quote.db' or os.path.exists(filename):
        return False

    csvFile = file(filename, 'wb')
    csvWriter = csv.writer(csvFile, dialect='excel')

    # 写入抬头信息
    title = ['id'] + list(Constant.QUOTATION_STRUCTURE)
    csvWriter.writerow(title)

    # db文件操作
    db = sqlite3.connect(dbFile)
    dbCursor = db.cursor()
    try:
        results = dbCursor.execute('select * from quotation')# 正序方式查询
        ret = results.fetchall()
        # db查询条目插入到csv文件中。
        for item in ret:
            csvWriter.writerow(item)
    except (Exception),e:
        Trace.output("fatal", " translate Exception: " + e.message)
    csvFile.close()
    dbCursor.close()
    db.close()
    return True

def sort_quote_csv(quoteCsvFile):
    """ 外部接口API:行情csv文件排序及条目去重。
        quoteCsvFile: 行情csv文件（含文件路径）
    """
    data = pd.read_csv(quoteCsvFile)
    #统一时间格式
    for row in data.itertuples():
        if data.ix[row.Index,'time'].find('/')!=-1:
            data.ix[row.Index,'time'] = data.ix[row.Index,'time'].replace('/','-')
        if len(data.ix[row.Index,'time'].split(':')) == 2:
            data.ix[row.Index,'time'] = data.ix[row.Index,'time']+':00'

    #增加dt2num列
    columnDt2num = []
    for tm in np.array(data['time']):
        columnDt2num.append(date2num(datetime.datetime.strptime(tm,"%Y-%m-%d %H:%M:%S")))
    data['clmndt2num']=columnDt2num
    #第一次排序
    data = data.sort_index(axis=0,ascending=True,by='clmndt2num')

    pureDf = DataFrame(columns=['period',]+list(Constant.QUOTATION_STRUCTURE)+['clmndt2num'])
    #按周期筛选
    for period in Constant.QUOTATION_DB_PREFIX:
        dataPickup = data[data['period']==period]
        preTime = ''
        dataPickup.is_copy = False
        for row in dataPickup.itertuples():
            if preTime == row.time:
                dataPickup.drop(row.Index,inplace=True)
            else:
                preTime = row.time
        pureDf = pureDf.append(dataPickup)#按周期叠加

    #第二次排序
    pureDf = pureDf.sort_values(axis=0,ascending=True,by='clmndt2num')
    pureDf.drop(['clmndt2num'],axis=1,inplace=True)#删除附属dt2num列
    purefile = quoteCsvFile.split('.')[0]+"-pure.csv"
    pureDf.to_csv(purefile,columns=['period',]+list(Constant.QUOTATION_STRUCTURE),index=False)
