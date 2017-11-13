#coding=utf-8

# 数据源url枚举的元组。按照优先级（报价精度）由高到低的顺序排列。
URL_SRC_LIST = ['Fx678','EastMoney']

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
SINA_XAU_JS_URL = 'http://hq.sinajs.cn/&list=hf_XAU'
#伦敦银报价URL
SINA_XAG_JS_URL = 'http://hq.sinajs.cn/&list=hf_XAG'

#汇通网报价
#黄金报价URL
FX678_XAU_URL = 'http://api.q.fx678.com/quotes.php?exchName=WGJS&symbol=XAU'
#白银报价URL及关键字段
FX678_XAG_URL = 'http://api.q.fx678.com/quotes.php?exchName=WGJS&symbol=XAG'
# 开盘价 --- p
# 最新价 --- b
# 最高价 --- h
# 最低价 --- l
# 时间戳 --- t
# 买入价 --- b
# 卖出价 --- se

#东方财富网
#EASTMONEY_XAG_URL = 'http://quote.eastmoney.com/globalfuture/SI00Y.html'
#动态抓取报价
EASTMONEY_URL_FRAGMENT1 = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._SG&sty=MPNSBAS&st=c&sr=-1&p=1&ps=5&cb=jQuery'
EASTMONEY_URL_FRAGMENT2 = '&js=([(x)])&token=7bc05d0d4c3c22ef9fca8c2a912d779c'
# 未知因素！
EASTMONEY_URLUNKNOW_TIMESTAMP = "17209736178267005318_"
#'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._SG&sty=MPNSBAS&cb=jQuery17209079031754561993_1510125297769&js=([(x)])&token=7bc05d0d4c3c22ef9fca8c2a912d779c'