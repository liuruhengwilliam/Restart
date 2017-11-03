#coding=utf-8

import time

# 夏令时和冬令时的闭市时间应该有所区别
CLOSING_BEGIN_TIME=4
CLOSING_END_TIME=6

# 数据抓取模块应该设定在每周一凌晨6点开始启动。这样能够兼顾到各周期记录（不遗漏）。

class Constant():
    """ 软件版本，行业相关术语等定义 """
    def __init__(self):
        return

    def get_version_info(self):
        """ 外部接口API: """
        print "Version Code: V0.2.4\n"+"Build Time: %s"%time.strftime("%Y-%m-%d %H:%M",time.localtime())

    def is_closing_market(self):
        """ 外部接口API:判断当前时间是否为闭市时间 """
        # 每工作日凌晨5点到6点为结算时间
        hour = time.strftime("%H",time.localtime())
        if int(hour) > CLOSING_BEGIN_TIME and int(hour) < CLOSING_END_TIME:
            return True

        return False