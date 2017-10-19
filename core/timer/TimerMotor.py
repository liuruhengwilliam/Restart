#coding=utf-8

import sys
import datetime
from LoopTimer import LoopTimer
from IntervalTimer import IntervalTimer

#循环定时器周期
#数据抓取两级定时器：快周期和慢周期定时器
FAST_LOOP_PERIOD = 10 #5 second
SLOW_LOOP_PERIOD = 300 #5 minute

#链式定时器周期
CHAIN_PERIOD = [1800,1*3600,2*3600,4*3600,6*3600,12*3600,24*3600,24*5*3600]

class TimerMotor():
    """ 定时器引擎 """
    def __init__(self, fastTimerFunc, slowTimerFunc, chainTimerFunc):
        """ 初始化三种定时器（链）"""
        self.fastTimer = self.slowTimer = self.chainTimer = None
        self.fastTimerFunc = fastTimerFunc
        self.slowTimerFunc = slowTimerFunc
        self.chainTimerFunc = chainTimerFunc

    def start_timer(self):
        """  启动定时器 """
        self.fastTimer = LoopTimer(FAST_LOOP_PERIOD, self.fastTimerFunc)
        self.fastTimer.start()

        self.slowTimer = LoopTimer(SLOW_LOOP_PERIOD, self.slowTimerFunc)
        self.slowTimer.start()

        self.chainTimer = IntervalTimer(0, self.chainTimerFunc,CHAIN_PERIOD)
        self.chainTimer.start()

    def get_fast_timer(self):
        return self.fastTimer

    def get_fastTM_cbfunc_result(self):
        """获取快速定时器回调函数返回值"""
        return self.fastTimer.get_cb_func_result()

    def get_slow_timer(self):
        return self.slowTimer

    def get_slowTM_cbfunc_result(self):
        """获取慢速定时器回调函数返回值"""
        return self.slowTimer.get_cb_func_result()

    def get_chain_timer(self):
        return self.chainTimer

    def get_chainTM_cbfunc_result(self):
        """获取链式定时器回调函数返回值"""
        return self.chainTimer.get_cb_func_result()
