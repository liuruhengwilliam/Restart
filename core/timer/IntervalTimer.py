#coding=utf-8

import threading
import time
import sys
import datetime

class IntervalTimer(threading._Timer):
    """ 变周期定时器类。该类继承threading._Timer类（详情可查看文件threading.py），并重构run()方法。
        Call a function with a Timer tuple ( parameter 'args[]' defined specified number of seconds):
            t = IntervalTimer(mess, f, args=[], kwargs={})
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting
    """
    def __init__(self, index, function, args=[], kwargs={}):
        threading._Timer.__init__(self, index, function, args=[], kwargs={})
        self.timerTuple = args
        self.timerIndex = index
        self.dumpFlag = True
        self.funcResult = None#回调函数的返回值

    def run(self):
        '''override run function'''
        try:
            for i in list(self.timerTuple):
                self.finished.wait(i)
                if self.finished.is_set():
                    self.finished.set()
                    break
                self.dump()
                self.funcResult = self.function(*self.args, **self.kwargs)
                self.timerIndex += 1
        except Exception,e:
            print "Exception: "+e.Message

    def getCBFuncResult(self):
        """获取回调函数返回值"""
        return self.funcResult

    def queryChainNode(self):
        return self.timerIndex

    def setDump(self,flag):
        self.dumpFlag = flag

    def dump(self):
        if self.dumpFlag:
            print "Timer %d" % self.timerIndex+" expired at %s" % datetime.datetime.now()
