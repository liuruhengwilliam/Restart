#coding=utf-8

import sys
#sys.path.append("..")
from engine.DataScrape import *
from timer.TimerMotor import *

def idiot():
    print "idiot"

def main():
    '''main routine'''
    dtScrp = DataScrape()
    tm = TimerMotor(dtScrp.queryInfo,dtScrp.idiot,dtScrp.idiot)

    tm.startTimer()

if __name__ == '__main__':
    main()
