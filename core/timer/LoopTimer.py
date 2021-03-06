#coding=utf-8

import threading
import time
import sys
import datetime
from resource import Trace

class LoopTimer(threading._Timer):
    """ 循环定时器类。该类继承threading._Timer类（详情可查看文件threading.py），并重构run()方法。
        具体用法如下：
        Call a function after a specified number of seconds:
            t = LoopTimer(30.0, f, args=[], kwargs={})
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting
    """
    def __init__(self, interval, function, args=[], kwargs={}):
        threading._Timer.__init__(self, interval, function, args=[], kwargs={})
        self.funcResult = None#回调函数的返回值

    def run(self):
        """override run function"""
        while True:
            self.finished.wait(self.interval)
            if self.finished.is_set():
                self.finished.set()
                break
            self.dump()
            #记录回调函数返回值
            self.funcResult = self.function(*self.args, **self.kwargs)

    def get_cb_func_result(self):
        """获取回调函数返回值"""
        return self.funcResult

    def dump(self):
        Trace.output('info',"Timer %s"%threading.currentThread().getName()+\
                     " expired at %s" % datetime.datetime.now())
