#coding=utf-8

import time

#夏令时和冬令时的闭市时间有所区别
CLOSING_BEGIN_TIME=4
CLOSING_END_TIME=7

class Constant():
    """ 行业相关术语等定义 """
    def __init__(self):
        return

    def is_closing_market(self):
        """ 判断当前时间是否为闭市时间 """
        hour = time.strftime("%H",time.localtime())
        if int(hour) > CLOSING_BEGIN_TIME and int(hour) < CLOSING_END_TIME:
            return True
        else:
            return False