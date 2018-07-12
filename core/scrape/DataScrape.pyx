#coding=utf-8

import re
import sys
import json
import time
import requests
import urllib2
import datetime
import traceback
from resource import Trace
from resource import Configuration

#金十报价墙
JIN10_PRICE_WALL = 'https://www.jin10.com/price_wall/index.html'

#和讯网白银报价URL
HEXUN_XAG_URL = 'http://quote.forex.hexun.com/2010/Data/FRunTimeQuote.ashx?code=XAGUSD&&time=142330'
#汇通网报价
#黄金报价URL
FX678_XAU_URL = 'http://api.q.fx678.com/getQuote.php?exchName=WGJS&symbol=XAU'
#白银报价URL及关键字段
FX678_XAG_URL = 'http://api.q.fx678.com/getQuote.php?exchName=WGJS&symbol=XAG'
# 开盘价 --- p
# 最新价 --- b
# 最高价 --- h
# 最低价 --- l
# 时间戳 --- t
# 买入价 --- b
# 卖出价 --- se
FX678_REQUEST_HEADER = {
    'Accept':'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Host':'api.q.fx678.com',
    'Origin':'http://quote.fx678.com',
    'Referer':'http://quote.fx678.com/symbol/XAG',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
}

def fx678_deal_with_query():
    """ 汇通网数据抓取处理函数
        返回值：列表结构---浮点型实时价格，时间字符串
    """
    ret_list = [] # 待返回的数据列表
    try:
        #数据请求
        r = requests.get(FX678_XAG_URL,headers=FX678_REQUEST_HEADER)
        if r.status_code != 200:
            return ret_list

        response_data = json.loads(r.text)
        close_price = str(response_data['c']).strip('[u\'\']')
        #time_stamp = str(response_data['t']).strip('[u\'\']')
        #时间戳转datatime结构
        #stampDt = datetime.datetime.fromtimestamp(float(time_stamp))
        # 为减少后续异常逻辑分支的处理，用当前PC时间取代网络时间戳
        ret_list = [float(close_price),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    except (Exception),e:
        exc_type,exc_value,exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
        traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))
    finally:
        return ret_list

#新浪网报价
XAU_URL='http://finance.sina.com.cn/futures/quotes/XAU.shtml'#伦敦金界面
XAG_URL='http://finance.sina.com.cn/futures/quotes/XAG.shtml'#伦敦银界面
SINA_XAU_JS_URL = 'http://hq.sinajs.cn/?_=%s/&list=hf_XAU'#伦敦金报价URL
SINA_XAG_JS_URL = 'http://hq.sinajs.cn/?_=%s/&list=hf_XAG'#伦敦银报价URL

def sinafinance_deal_with_query():
    """ 新浪财经数据抓取处理函数。
        返回值: 列表结构---实时价格（浮点型），当前时间字符串
    """
    ret_list = [] # 待返回的数据列表
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
    sinafinance_url = SINA_XAG_JS_URL%str((time.time())*1000)

    try:
        #构造数据请求
        req = urllib2.Request(sinafinance_url, None, fake_simple_head)
        #接收响应数据报文
        response = urllib2.urlopen(req).read()
        #数据进行切片分析
        close_price = response.split('"')[1].split(',')[0]
        ret_list = [float(close_price),datetime.datetime.now().strftime('%Y-%m%-d %H:%M:%S')]
    except (Exception),e:
        exc_type,exc_value,exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
    finally:
        return ret_list

def query_info_futures():
    """ 外部接口API：获取某网站相关期货/现货信息 """
    #每个数据源采集的字典结构可能(基本都)会不同，但是统一返回两项值：当前价格(浮点型)和当前时间字符串。

    for dataSrc in ('Fx678','SinaFinance'):
        retList = []
        if dataSrc == 'Fx678':#高优先级排前
            retList = fx678_deal_with_query()
        else:#低优先级排后
            retList = sinafinance_deal_with_query()
        if len(retList) == 2:
            Trace.output('debug',"From %s, quote the price of %s at %s"%(dataSrc,retList[0],retList[1]))
            break
    else:
        Trace.output('fatal',"Failed to query price on DataScrape module from ALL OF DATASOURCE!")

    return retList

#=======================================================================================================#

#东方财富网
#EASTMONEY_XAG_URL = 'http://quote.eastmoney.com/globalfuture/SI00Y.html'

EASTMONEY_URL_FRAGMENT='http://mdfm.eastmoney.com/EM_UBG_MinuteApi/Js/Get?dtype=25&style=tail&check=st&dtformat=HH:mm:ss&num=10'
#沪市002开头股票(比如：赣锋锂业002460)在其后添加'&id=0024602'
#深市600开头股票(比如：中航电子600372)在其后添加'&id=6003721'
#'http://mdfm.eastmoney.com/EM_UBG_MinuteApi/Js/Get?dtype=25&style=tail&check=st&dtformat=HH:mm:ss&id=6003721&num=10'

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
        traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))
    finally:
        return response

def query_info_stock(stockID):
    """ 外部接口API: 获取相关信息
        stockID: 股票代码的字符串
        返回值：Constant.QUOTATION_STRUCTURE列表结构
              (time--string,open--float,high--float,low--float,close--float)
    """
    ret = None
    if stockID.startswith('600') or stockID.startswith('601') or stockID.startswith('603'):
        ret = deal_with_stock_query(EASTMONEY_URL_FRAGMENT+'&id=%s'%stockID+'1')
    elif stockID.startswith('000') or stockID.startswith('002') or stockID.startswith('300'):
        ret = deal_with_stock_query(EASTMONEY_URL_FRAGMENT+'&id=%s'%stockID+'2')
    if ret is None:
        return None

    # 正则表达式挑选 "data":开头，且在中括号内的信息
    retsearch = re.search(r'"data":\[(.*)\]',ret)
    if retsearch is None or retsearch.group(1) is None:
        Trace.output('fatal',"Failed to filter stock(%s) Data from %s!"%(stockID,ret))
        return None

    timeList = []
    priceList = []
    # 逗号分隔符作为标志返回列表
    pickuplist = retsearch.group(1).split(',')
    for item in pickuplist:
        # 正则表达式挑选 "t":开头，且在双引号内的信息--时间
        time = re.search(r'"t":"(.*)"',item)
        # 正则表达式挑选 "p":开头，且在双引号内的信息--价格
        price = re.search(r'"p":"(.*)"',item)
        if time is not None and time.group(1) is not None:
            timeList.append(time.group(1))
        if price is not None and price.group(1) is not None:
            priceList.append(float(price.group(1)))
    # 添加年月日信息
    dt = datetime.datetime.now()
    date = '%s-%s-%s '%(dt.strftime('%Y'),dt.strftime('%m'),dt.strftime('%d'))

    if len(timeList)==0 or len(priceList)==0 or float(max(priceList))==0 or float(min(priceList))==0:
        return None
    retList = [date+str(timeList[0]),float(priceList[-1]),float(max(priceList)),float(min(priceList)),float(priceList[0])]
    #Trace.output('debug',stockID+':'+' '.join(map(lambda x:str(x), retList)))
    return retList
