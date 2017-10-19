#coding=utf-8

import sys
import time
from DataSource import *
import requests
import re

class DataScrape():
    """ 数据抓取类 """
    def __init__(self):
        self.dumpFlag = False
        self.dataSource = DataSource()

    def query_info(self):
        """ 获取某网站相关信息 """
        #每个数据源采集的字典结构可能(基本都)会不同
        infoDict = {}
        url = self.dataSource.get_source()

        #每个网站采集到的信息格式不同，需要加以区分
        if url == self.dataSource.FX678_XAG_URL:
            try:
                #数据请求
                r = requests.get(url)
                #数据进行切片分割
                content = r.text.split('{')[1].split('}')[0].split(',')
                if self.dumpFlag: print content
                tag =[]
                value = []

                for item in content:
                    tag.append(item.split(':')[0])
                    value.append(item.split(':')[1].strip('[""]'))
                    #转化成字典格式保存
                    infoDict = dict(zip(tag,value))

                if self.dumpFlag: print infoDict

            except (Exception),e:
                print "DataScrape Exception: "+e.message

        return [infoDict[u'"p"'],infoDict[u'"b"'],infoDict[u'"h"'],infoDict[u'"l"'],\
         time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(infoDict[u'"t"'])))]

    def set_dump(self,flag):
        self.dumpFlag = flag

