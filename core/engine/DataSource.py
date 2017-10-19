#coding=utf-8

class DataSource():
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

    def __init__(self):
        self.dataSource = self.FX678_XAG_URL #as default

    def get_source(self):
        return self.dataSource

    def set_source(self,source):
        self.dataSource = source
