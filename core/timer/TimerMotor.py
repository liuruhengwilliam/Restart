#coding=utf-8

from LoopTimer import LoopTimer

"""
    定时器引擎类
"""
""" 外部接口API:初始化三种定时器（链）。
    周期定时器具有相同定时逻辑：即同时启动一个（组）周期定时器。
"""

def start_loop_timer(tmFunc, Period):
    """  外部接口API:启动周期定时器
        timerFunc：为定时器回调函数列表
        Period：固定周期定时列表 """
    fastenTimer = []#固定周期定时器列表
    if len(Period) != 0:
        for (period,func) in zip(Period, tmFunc):
            tmpTimer = LoopTimer(period, func)
            tmpTimer.start()
            # 添加到固定周期定时器列表中
            fastenTimer.append(tmpTimer)

