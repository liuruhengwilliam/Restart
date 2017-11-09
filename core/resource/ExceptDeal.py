#coding=utf-8

import datetime

def is_weekend():
    """ 是否周末---周末闭市 """
    now = datetime.datetime.now()
    day, hour = now.isoweekday(),now.strftime("%H")
    if(int(day) == 6 and int(hour) > 5) or int(day) == 7:
        return True
    return False

def exit_on_weekend(workWeek):
    """ 到周末就退出 """
    curWeek = (datetime.datetime.now()).strftime('%U')
    if curWeek != workWeek:
        return True

    return is_weekend()

class engineException(Exception):
    """数据引擎模块自定义异常"""
    def __init__(self,err='engine Exception'):
        Exception.__init__(self,err)