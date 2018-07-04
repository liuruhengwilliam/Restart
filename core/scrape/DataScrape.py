#coding=utf-8

import re
import sys
import datetime
import DataSource
import Fx678
import EastMoney
import SinaFinance
from resource import Trace
from resource import Configuration

def query_info_futures():
    """ 外部接口API：获取某网站相关期货/现货信息 """
    #每个数据源采集的字典结构可能(基本都)会不同，但是统一返回两项值：当前价格(浮点型)和当前时间字符串。

    for dataSrc in DataSource.URL_SRC_TUPLE:
        retList = []
        if dataSrc == 'Fx678':#高优先级排前
            retList = Fx678.deal_with_query()
        else:#低优先级排后
            retList = SinaFinance.deal_with_query()
        if len(retList) == 2:
            Trace.output('debug',"From %s, quote the price of %s at %s"%(dataSrc,retList[0],retList[1]))
            break
    else:
        Trace.output('fatal',"Failed to query price on DataScrape module from ALL OF DATASOURCE!")

    return retList

def query_info_stock(stockID):
    """ 外部接口API: 获取相关信息
        stockID: 股票代码的字符串
        返回值：Constant.QUOTATION_STRUCTURE列表结构
              (time--string,open--float,high--float,low--float,close--float)
    """
    ret = None
    if stockID.startswith('600') or stockID.startswith('601') or stockID.startswith('603'):
        ret = EastMoney.deal_with_stock_query(DataSource.EASTMONEY_URL_FRAGMENT+'&id=%s'%stockID+'1')
    elif stockID.startswith('000') or stockID.startswith('002') or stockID.startswith('300'):
        ret = EastMoney.deal_with_stock_query(DataSource.EASTMONEY_URL_FRAGMENT+'&id=%s'%stockID+'2')
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

    if len(timeList) == 0 or len(priceList) == 0:
        return None
    retList = [date+str(timeList[0]),float(priceList[-1]),float(max(priceList)),float(min(priceList)),float(priceList[0])]
    #Trace.output('debug',stockID+':'+' '.join(map(lambda x:str(x), retList)))
    return retList
