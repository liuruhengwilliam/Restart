#coding=utf-8

import sys
import time
import requests
import re
import traceback
import DataSource

class DataScrape():
    """ 数据抓取类 """
    def __init__(self):
        self.dumpFlag = False
        self.url = DataSource.FX678_XAG_URL

    def query_info(self):
        """ 外部接口API：获取某网站相关信息 """
        #每个数据源采集的字典结构可能(基本都)会不同
        infoDict = {}
        retList = [] # 待返回的数据列表

        #每个网站采集到的信息格式不同，需要加以区分
        if self.url == DataSource.FX678_XAG_URL:
            try:
                #数据请求
                r = requests.get(self.url)
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
                # 用"最新价( b )"刷新各周期数据库
                retList = [infoDict[u'"p"'],infoDict[u'"b"'],infoDict[u'"h"'],infoDict[u'"l"'],\
                        time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(infoDict[u'"t"'])))]
            except (Exception),e:
                exc_type,exc_value,exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_tb)
            finally:
                return retList


