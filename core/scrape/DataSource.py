#coding=utf-8

# 数据源url枚举的元组。按照优先级（报价精度）由高到低的顺序排列。
URL_SRC_TUPLE = ('Fx678','SinaFinance')
URL_SRC_DEFAULT = URL_SRC_TUPLE[0]
"""数据源等相关内容的定义和归纳"""
#金十报价墙
JIN10_PRICE_WALL = 'https://www.jin10.com/price_wall/index.html'
#安全socket连接中包含报价信息
#https://ssgfcfkdll.jin10.com:9081/socket.io/?EIO=3&transport=polling&t=LxSsrnb&sid=CI8hf7hc-WLfuazjABqN

#新浪网报价
#伦敦金界面
XAU_URL='http://finance.sina.com.cn/futures/quotes/XAU.shtml'
#伦敦银界面
XAG_URL='http://finance.sina.com.cn/futures/quotes/XAG.shtml'

#伦敦金报价URL
SINA_XAU_JS_URL = 'http://hq.sinajs.cn/?_=%s/&list=hf_XAU'
#伦敦银报价URL
SINA_XAG_JS_URL = 'http://hq.sinajs.cn/?_=%s/&list=hf_XAG'

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

#东方财富网
#EASTMONEY_XAG_URL = 'http://quote.eastmoney.com/globalfuture/SI00Y.html'

EASTMONEY_URL_FRAGMENT='http://mdfm.eastmoney.com/EM_UBG_MinuteApi/Js/Get?dtype=25&style=tail&check=st&dtformat=HH:mm:ss&num=10'
#沪市002开头股票(比如：赣锋锂业002460)在其后添加'&id=0024602'
#深市600开头股票(比如：中航电子600372)在其后添加'&id=6003721'
#'http://mdfm.eastmoney.com/EM_UBG_MinuteApi/Js/Get?dtype=25&style=tail&check=st&dtformat=HH:mm:ss&id=6003721&num=10'

#和讯网
#白银报价URL
HEXUN_XAG_URL = 'http://quote.forex.hexun.com/2010/Data/FRunTimeQuote.ashx?code=XAGUSD&&time=142330'