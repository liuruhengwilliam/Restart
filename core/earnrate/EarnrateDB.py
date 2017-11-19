#coding=utf-8

import os
import sqlite3
import datetime
from resource import Configuration
from resource import Primitive
from resource import Trace

class EarnrateDB():
    """
        胜率数据库：
            功能描述：
                协作模块初始化数据库（搭建数据库结构）
                由strategy模块进行插入（条目的前若干字段，比如：多/空，判定周期，时间）操作。
                chain定时器（Start类中启动）进行更新（操作策略之后若干周期时间点的盈利情况）。
            接口API：
                初始化
                插入
                查询
                更新
    """

    def create_earnrate_db(self):
        """ 外部接口API: 创建数据库文件 """
        dt = datetime.datetime.now()
        year,week = dt.strftime('%Y'),dt.strftime('%U')
        fileName = year+'-'+week+'earnrate.db'
        file = Configuration.get_working_directory()+'/'+fileName
        # 生成数据库文件
        isExist = os.path.exists(file)
        db = sqlite3.connect(file)
        dbCursor = db.cursor()
        #First: create db if empty
        if not isExist:
            try:
                dbCursor.execute(Primitive.EARNRATE_DB_CREATE)
            except (Exception),e:
                Trace.output('fatal',"create earnrate db file Exception: "+e.message)
        db.commit()
        dbCursor.close()
        db.close()
