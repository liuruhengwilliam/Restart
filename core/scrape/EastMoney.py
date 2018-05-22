#coding=utf-8
import sys
import time
import datetime
import requests
import urllib2
import traceback


def deal_with_stock_query(stock_url):
    """ 东方财富网数据抓取处理函数 """
    response = None
    #now_timestamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    #下面复杂报文头暂时未使用
    fake_complex_head = {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Host':'hq.sinajs.cn',
    'If-None-Match':'W/"ICiAA1aWG7F"',
    'Referer':'http://finance.sina.com.cn/futures/quotes/XAG.shtml',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    }
    fake_simple_head = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'
    }

    try:
        #构造数据请求
        req = urllib2.Request(stock_url, None, fake_simple_head)
        #接收响应数据报文
        response = urllib2.urlopen(req).read()
    except (Exception),e:
        exc_type,exc_value,exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
    finally:
        return response
