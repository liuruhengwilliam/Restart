#coding=utf-8

import sqlite3

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