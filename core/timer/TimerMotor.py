#coding=utf-8

from LoopTimer import LoopTimer
from IntervalTimer import IntervalTimer

class TimerMotor():
    """ 定时器引擎 """
    def __init__(self):
        """ 外部接口API:初始化三种定时器（链）。
            cacheTimer和arrayTimer定时器具有相同定时逻辑：即同时启动一个（组）周期定时器。
            chainTimer定时器逻辑：前一个定时器到期之后再去设置下一个定时器。"""

        # fastenTimer是一组定时器。定时器的起始时间是相同的。
        self.fastenTimer = []# 固定周期定时器列表
        self.fastenTimerPeriod = [] # 固定周期定时器时间列表
        self.fastenTimerFunc = [] # 固定周期定时器回调函数列表。回调函数可能不同。

        # chainTimer是一个定时器。一个定时周期会变化的定时器。
        self.chainTimer = None
        self.chainTimerPeriod = [] # 链式周期定时器时间列表
        self.chainTimerFunc = None

    def init_fasten_timer(self, tmFunc , period):
        """ 外部接口API:初始化一个（组）固定周期定时器。
            timerFunc：为定时器回调函数列表
            period：固定周期定时列表 """
        self.fastenTimerFunc = tmFunc
        self.fastenTimerPeriod = period

    def init_chain_timer(self, timerFunc , period):
        """ 外部接口API:初始化一个（组）固定周期定时器。
            timerFunc：为定时器回调函数
            period：链式周期定时列表 """
        self.chainTimerFunc = timerFunc
        self.chainTimerPeriod = period

    def start_timer(self):
        """  外部接口API:启动定时器 """
        if len(self.fastenTimerPeriod) != 0:
            for (period,func) in zip(self.fastenTimerPeriod, self.fastenTimerFunc):
                tmpTimer = LoopTimer(period, func)
                tmpTimer.start()
                # 添加到固定周期定时器列表中
                self.fastenTimer.append(tmpTimer)

        if len(self.chainTimerPeriod) != 0:
            self.chainTimer = IntervalTimer(0, self.chainTimerFunc,self.chainTimerPeriod)
            self.chainTimer.start()

    def get_fasten_timer(self):
        return self.fastenTimer

    def get_chain_timer(self):
        return self.chainTimer
