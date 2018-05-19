#coding=utf-8

import os
import csv
import sqlite3
import datetime
import numpy as np
import pandas as pd
from pandas import DataFrame
from resource import Configuration
from resource import Constant
from resource import Trace

def supplement_quotes(path,dataWithID,supplementCnt):
    """ 外部接口API：补齐某个数目的行情序列。不考虑*.csv格式文件转换（可手动编辑）。
        path：路径字符串
        dataWithID: 当前周期行情数据库文件的dataframe结构数据
        supplementCnt: 需要增补的数目
        返回值: 增补后的dateframe结构行情数据
    """
    weekGap = 1 # 从前一周开始搜索
    period = Configuration.get_field_from_string(path)[-2]
    while supplementCnt > 0:
        preDBfile = Configuration.get_back_week_period_directory(path,weekGap)+period+'-quote.csv'
        if not os.path.exists(preDBfile): #若回溯文件完毕，则退出循环。
            break

        dataSupplementWithID = pd.read_csv(preDBfile)
        if dataSupplementWithID is None or len(dataSupplementWithID) == 0:
            #对于无记录文件情形，dataSupplementCnt为空Series。int(dataSupplementCnt)会报错。
            supplCnt = 0
        else:
            dataSupplementCnt = dataSupplementWithID.iloc[-1:]['id']
            supplCnt = int(dataSupplementCnt)

        if supplCnt >= supplementCnt: #已经能够补全，取后面的(supplementCnt)个数据
            dataSupplement = dataSupplementWithID.iloc[supplCnt-supplementCnt:]
        elif dataSupplementWithID is None:
            dataSupplement = None
        else: #还未补全数据继续循环
            dataSupplement = dataSupplementWithID

        weekGap+=1 #时间回溯
        supplementCnt-=supplCnt #待补全的数据调整。若为负，则跳出循环。
        if dataSupplement is not None:
            dataWithID = dataSupplement.append(dataWithID,ignore_index=True) #按照时间顺序收集合并数据

    return dataWithID

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
