#coding=utf-8
import os
from timer import TimerMotor
from resource import Constant
from resource import Trace
from resource import Configuration
from strategy.ClientMatch import ClientMatch

Configuration.create_working_directory() #创建工作目录

def client_main():
    #在Linux平台下可以利用while命令循环执行shell命令
    #参考文档：http://blog.csdn.net/daoshuti/article/details/72831256
    if Constant.is_closing_market():
        return
    if Constant.is_weekend():
        os._exit(0) #退出Python程序

    path = Configuration.get_property("dependDataPath")
    if path == None:
        Trace.output('fatal','no data path depended!')
        return
    clientMatchHdl = ClientMatch(path)

    #也可使用配置文件设置循环定时器的方式
    clientPeriod = Configuration.get_property("clientPeriod")#单位是秒
    if clientPeriod == None:
        clientPeriod = Constant.QUOTATION_DB_PERIOD[1]
    TimerMotor.start_loop_timer((clientMatchHdl.match_KLineIndicator,),[int(clientPeriod),])

if __name__ == '__main__':
    client_main()
