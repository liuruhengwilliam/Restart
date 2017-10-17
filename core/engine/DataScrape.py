#coding=utf-8

import sys
#sys.path.append("..")
from DataSource import *
import requests
import re

class DataScrape():
    """ 数据抓取类 """
    def __init__(self):
        self.dumpFlag = True
        self.dataSource = DataSource()

    def queryInfo(self):
        ''' 获取某网站相关信息 '''
        url = self.dataSource.querySource()
        #每个网站采集到的信息格式不同，需要加以区分
        if url == self.dataSource.FX678_XAG_URL:
            try:
                r = requests.get(url)
                content = r.text.split('{')[1].split('}')[0].split(',')
                if self.dumpFlag: print content
                tag,value = []

                for item in content:
                    tag.append(item.split(':')[0])
                    #转化成字典格式保存
                    value.append(item.split(':')[1].strip('[""]'))

                    infoDict = dict(zip(tag,value))
                    if self.dumpFlag: print infoDict

            except (Exception),e:
                print "Exception: "+e.message
                return ""

    def setDump(self,flag):
        self.dumpFlag = flag

    def idiot(self):
        print "idiot"