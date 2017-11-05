#coding=utf-8

import csv
import sqlite3
from resource import Primitive

def translate_db_into_csv(filePath, lineCnt):
    """ 外部接口API:将db文件转换成csv文件
        filePath: db文件名（含文件路径）
        lineCnt: 截取db条目数目
    """
    csvFile = file(filePath.split('.')[0] + '.csv', 'wb')
    csvWriter = csv.writer(csvFile, dialect='excel')

    # db文件操作
    db = sqlite3.connect(filePath)
    dbCursor = db.cursor()
    try:
        results = dbCursor.execute(Primitive.QUOTATION_DB_QUERY)
        ret = results.fetchall()
        # db查询条目插入到csv文件中。后续可以根据lineCnt进行截取。
        for item in ret:
            csvWriter.writerow(item)
    except (Exception),e:
        print " translate quotation Exception: " + e.message
    csvFile.close()
    db.commit()
    dbCursor.close()
    db.close()

def tranlate_list_to_csv(fileName,listToDeal):
    """ 外部接口API:将列表转换成csv文件
        fileName: csv文件名（含文件路径）
        listToDeal: 列表
    """
    csvFile = file(fileName, 'wb')
    csvWriter = csv.writer(csvFile, dialect='excel')
    for item in listToDeal:
        csvWriter.writerow(item)
    csvFile.close()


