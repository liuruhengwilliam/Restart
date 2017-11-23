#coding=utf-8

import threading
import time
import sys
import datetime
from resource import Trace

class IntervalTimer(threading._Timer):
    """ 变周期定时器类。该类继承threading._Timer类（详情可查看文件threading.py），并重构run()方法。
        Call a function with a Timer tuple ( parameter 'args[]' defined specified number of seconds):
            t = IntervalTimer(mess, f, args=[], kwargs={})
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting
    """
    def __init__(self, index, function, args=[], kwargs={}):
        threading._Timer.__init__(self, 0, function, args=[], kwargs={})
        self.timerTuple = args
        self.dbItemId = index

    def run(self):
        '''override run function'''
        try:
            for i in list(self.timerTuple):
                self.finished.wait(i)
                if self.finished.is_set():
                    self.finished.set()
                    break
                self.dump()
                self.function(*self.args, **self.kwargs)
        except Exception,e:
            Trace.output('fatal', "Interval Timer Exception: "+e.Message)

    def dump(self):
        Trace.output('info',"Chain Timer No.%d" % self.dbItemId+" expired at %s" % datetime.datetime.now())
