#coding=utf-8

import threading
import time
import sys
import datetime
from resource import Trace
from resource import Constant

class LoopTimer(threading.Thread):
    """ 循环定时器类。该类继承threading.Thread类（详情可查看文件threading.py），并重构run()方法。
        具体用法如下：
        Call a function after a specified number of seconds:
            t = LoopTimer(30.0, f, args=[], kwargs={})
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting
    """
    def __init__(self, indx, period, func):
        """ 定时器初始化函数。
            period: 定时器超时时间。
            func: 定时器到期时回调函数。
        """
        self.func = func
        self.period = period
        self.tmName = Constant.QUOTATION_DB_PREFIX[indx]

        super(LoopTimer,self).__init__(name=self.tmName)

    def run(self):
        """ 覆盖Thread类的run()方法。注：不能执行基类的run()方法，否则会报错。
        """
        while True:
            time.sleep(float(self.period))
            self.func()
            self.dump()

    def dump(self):
        Trace.output('info',"Timer %s"%threading.currentThread().getName()+\
                     " expired at %s" % datetime.datetime.now())
