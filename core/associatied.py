#coding=utf-8

import sys

from engine.DataScrape import *
from timer.TimerMotor import *

#class core():
def idiot():
    print "idiot"

def core():
    '''main routine'''
    dtScrp = DataScrape()
    tm = TimerMotor(dtScrp.queryInfo,dtScrp.idiot,dtScrp.idiot)
    tm.startTimer()

    print tm.getFastTMCBFuncResult()


if __name__ == '__main__':
    core()
