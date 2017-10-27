#coding=utf-8

import datetime

class ExceptDeal():
    def is_weekend(self):
        """ 是否周末---周末闭市 """
        now = datetime.datetime.now()
        day, hour = now.isoweekday(),now.strftime("%H")
        if(day == "6" and hour > 5) or day == "7":
            return True
        return False