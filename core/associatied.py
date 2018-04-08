#coding=utf-8

import re
import os
import sys
import csv
import sqlite3
import time
import datetime
import threading
import talib
import pandas as pd
from pandas import DataFrame
import numpy as np
import requests
import urllib
import urllib2
import cookielib
import commands
import subprocess
import Tkinter
import tkMessageBox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
#from engine.DataScrape import *
#from timer.TimerMotor import *
#from quotation.QuotationDB import *
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
#from resource import Primitive
from resource import Constant
from resource import Configuration
#from strategy import Strategy
#from quotation import QuotationKit

event = threading.Event()
QUOTATION_DB_PREFIX = ['5min','15min','30min','1hour','2hour','4hour','6hour','12hour','1day','1week']
QUOTATION_DB_PERIOD = [5*60,15*60,30*60,1*3600,2*3600,4*3600,6*3600,12*3600,1*24*3600,5*24*3600]
QUOTATION_STRUCTURE = ['startPrice','realPrice','maxPrice','minPrice','time']

QUERY_ALL_SQL = 'select * from quotation'
QUERY_ID_SQL = 'select id from quotation'

#%matplotlib inline

def func():
    # 等待事件，进入等待阻塞状态
    print '%s wait for event...' % threading.currentThread().getName()
    event.wait()

    # 收到事件后进入运行状态
    print '%s recv event.' % threading.currentThread().getName()

def csv_test():
    if False:
        csvFile = 'D:/misc/future/2017-44/5min.csv'
        #挑取对应周期字典项
        csvFile = file(csvFile, 'wb')
        csvWriter = csv.writer(csvFile, dialect='excel')
        for item in [0,1]:
            csvWriter.writerow(item)
        csvFile.close()
    else:
        F15M_30M_1H = DataFrame(columns=Constant.SER_DF_STRUCTURE)
        csvFile = 'D:\\misc\\2018-11\\15min\\15min-ser2018-03-27.csv'
        csv_reader = csv.reader(open(csvFile, 'r'))
        #print pd.DataFrame(columns=Constant.SER_DF_STRUCTURE)
        for row in csv_reader:
            #print pd.concat(row,keys=Constant.SER_DF_STRUCTURE)
            if row != list(Constant.SER_DF_STRUCTURE):
                F15M_30M_1H = F15M_30M_1H.append(DataFrame(dict(zip(Constant.SER_DF_STRUCTURE,row)),index=[row[0],]))
            #print pd.DataFrame(dict(zip(Constant.SER_DF_STRUCTURE,row)),index=[0])
            #F15M_30M_1H = pd.DataFrame(row,columns=Constant.SER_DF_STRUCTURE,index=['a'])
        print (F15M_30M_1H)

def file_test():
    for line in open('D:/misc/future/2017-44/5min.db'):
        print line

def create_db_test():
    """ 外部接口API: 创建数据库文件 """
    dt = datetime.datetime.now()
    year,week = dt.strftime('%Y'),dt.strftime('%U')
    #各周期创建所属的策略盈亏率数据库
    for tagPeriod in Constant.QUOTATION_DB_PREFIX[1:]:
        filePath = 'D:\\misc\\2018-03\\1day\\1day-ser.db'
        #生成数据库文件
        isExist = os.path.exists(filePath)
        db = sqlite3.connect(filePath)
        dbCursor = db.cursor()
        #First: create db if empty
        if not isExist:
            try:
                dbCursor.execute(Primitive.STRATEARNRATE_DB_CREATE)
            except (Exception),e:
                print "create stratearnrate db file Exception: "+e.message
        db.commit()
        dbCursor.close()
        db.close()

def insert_db_test():
    """ 外部接口API:策略产生点时，插入该策略条目信息。
        可随同最小周期定时器调用。
        periodName: 周期名称字符串
        dfStrategy: DataFrame结构的策略数据
    """
    filePath = "D:\\misc\\2018-03\\1day\\1day-ser.db"
    db = sqlite3.connect(filePath)
    dbCursor = db.cursor()
    matchItem = ['1900-01-01:12:00',20.00,'1day','UNKNOWN',200,'',\
            0,'',10000,'',0,'',10000,'',0,'',10000,'',0,'',10000,'',0,'',10000,'',0,'',10000,'',0,'',10000,'']
    try:
        #刨开DataFrame中特有项
        dbCursor.execute(Primitive.STRATEARNRATE_DB_INSERT,matchItem)
    except (Exception),e:
        print "insert into stratearnrate db Exception: " + e.message

    db.commit()# 提交
    dbCursor.close()
    db.close()

def update_db_test():
    """ 外部接口API:更新某周期的策略盈亏率数据库。由‘5min’周期定时函数进行调用。
        periodName:周期名--字符串
        indxList:待更新条目序号的列表
        dfStrategy: DataFrame结构的策略数据
    """
    filePath = "D:\\misc\\2018-03\\1day\\1day-ser.db"
    db = sqlite3.connect(filePath)
    dbCursor = db.cursor()

    matchItem = ['2000-01-01:12:00',23.00,'1day','William',100,'',\
            0,'2010-01-01:13:00',10,'2010-01-01:14:00',0,'',10000,'',0,'',10000,'',0,'',10000,'',0,'',10000,'',0,'',10000,'',0,'',10000,'']
    try:
        dbCursor.execute('update stratearnrate set time=?,price=?,tmName=?,\
                patternName=?,patternVal=?,DeadTime=?,\
                M15maxEarn=?,M15maxEarnTime=?,M15maxLoss=?,M15maxLossTime=?,\
                M30maxEarn=?,M30maxEarnTime=?,M30maxLoss=?,M30maxLossTime=?,\
                H1maxEarn=?,H1maxEarnTime=?,H1maxLoss=?,H1maxLossTime=?,\
                H2maxEarn=?,H2maxEarnTime=?,H2maxLoss=?,H2maxLossTime=?,\
                H4maxEarn=?,H4maxEarnTime=?,H4maxLoss=?,H4maxLossTime=?,\
                H6maxEarn=?,H6maxEarnTime=?,H6maxLoss=?,H6maxLossTime=?,\
                H12maxEarn=?,H12maxEarnTime=?,H12maxLoss=?,H12maxLossTime=? \
                where indx=1',matchItem)
    except (Exception),e:
        print "update Earn in stratearnrate db Exception: "+e.message
    db.commit()
    dbCursor.close()
    db.close()

def db_test():
    dbFile = 'D:/misc/future/2017-44/5min.db'
    db = sqlite3.connect(dbFile)
    dbCursor = db.cursor()
    try:
        #results = dbCursor.execute(QUERY_ALL_SQL)
        results = dbCursor.execute('select * from quotation order by id desc')
        ret = results.fetchall()
        #ret = results.fetchmany(1)
    except (Exception),e:
        print "query in quotation db Exception: " + e.message
    db.commit()
    dbCursor.close()
    db.close()
    print ret, len(ret), max(list(ret[0]))
    return ret

def datetime_test():
    dt = datetime.datetime.now()
    #print str(int(dt.strftime('%U'))-1)
    #print int(dt.isoweekday())
    now = datetime.datetime.now()
    day, hour = now.isoweekday(),now.strftime("%H")

    timenow = time.localtime()
    #print day,hour
    #print dt.strftime('%H')
    #print dt.strftime('%Z')
    #for (tmp, name) in zip(QUOTATION_DB_PREFIX, QUOTATION_DB_PERIOD):
    #    print tmp,name

def dict_test():
    recordPeriodDict = {}
    dicttmp = {}
    atomicItem = dict(zip(QUOTATION_STRUCTURE,[0,0,0,0,'']))
    for tag in list(QUOTATION_DB_PERIOD):
        dicttmp = {tag: atomicItem}
        recordPeriodDict.update(dicttmp)

    print recordPeriodDict

def idiot():
    print "idiot"

def thread_test():
    '''main routine'''
    #dtScrp = DataScrape()
    #tm = TimerMotor(dtScrp.queryInfo,dtScrp.idiot,dtScrp.idiot)
    #tm.startTimer()

    #print tm.getFastTMCBFuncResult()
    t1 = threading.Thread(target=func)
    t2 = threading.Thread(target=func)
    t1.start()
    t2.start()

    time.sleep(2)
    # 发送事件通知
    #print 'MainThread set event.'
    event.set()

def sma_test():
    file = 'F:\\code\\python\\RESTART\\core\\2017\\2017-51\\15min\\15min.db' # 拼装文件路径和文件名
    dataWithId = Primitive.translate_db_to_df(file)
    smaData = dataWithId['close'].as_matrix()
    N = 5
    weights = np.ones(N)/N
    sma5 = np.convolve(weights,smaData)[N-1:-N+1]
    t = np.arange(N-1,len(smaData))
    #plt.plot(t,smaData[N-1:],lw=1.0,label='Data')
    plt.plot(t,sma5,'--',lw=2.0,label='Moving average')

    plt.grid()
    plt.legend()
    plt.show()

def talib_func():
    func_collection = talib.get_functions()
    for i in func_collection:
        print i

    func_dict = talib.get_function_groups()
    # 迭代器
    for item in func_dict.iteritems():
        print item

def talib_macd():
    """参考链接：https://www.cnblogs.com/hhh5460/p/5602357.html"""
    close = {'close':np.random.random(100)}
    macd,macdsignal,macdhist = talib.abstract.MACD(close,fastperiod=12,slowperiod=26,signalperiod=9)
    print '==== macd ====\n',macd
    print '\n==== macdsignal ====\n',macdsignal
    print '\n==== macdhist ====\n',macdhist

    real = talib.MOM(close['close'], timeperiod=10)
    print '\n==== real ====\n',real

def numpy_data():
    data_analyse = numpy.random.random(10)
    print type(data_analyse)

def talib_sma_test():
    data_analyse = {
        'open':numpy.random.random(100),
        'high':numpy.random.random(100),
        'low':numpy.random.random(100),
        'close':numpy.random.random(100),
        'volume':numpy.random.random(100)
    }
    #close = numpy.random.random(100)
    #output = talib.SMA(close)
    output = talib.abstract.SMA(data_analyse, timeperiod=20, price='open')
    print (output)

def talib_pattern_15min():
    file = 'F:\\code\\python\\RESTART\\core\\2017-51\\15min.db' # 拼装文件路径和文件名
    dataWithId = Primitive.translate_db_to_df(file)
    if dataWithId is None:
        raise ValueError
        return

    Strategy.check_strategy(2,file,dataWithId)

def get_property():
    """ 内部接口API：根据XML配置文件读取相关属性字段 """
    fileName = 'Properties.xml'

    if not os.path.exists(fileName):
        return

    try:
        tree = ET.parse(fileName)
        root = tree.getroot()
    except Exception,e:
        print e.message
        return

    print root.tag, "---", root.attrib
    for child in root:
        print child.tag,'---' , child.attrib,'---',type(child)
    print len(root)
    print root[0][0].text
    print root[1][0].text

    for item in root.findall("data"):
        print item.find('value').text

def query_info():
    """东方财富网"""
    unknow_timestamp = "17209736178267005318"
    time_tick_beijin = (int(time.time()))*1000
    #print (time_tick_beijin)
    ret_timestamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    ret_price = ''

    #eastmoney_url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._SG&sty=MPNSBAS&st=c&sr=-1&p=1&ps=5&cb=jQuery%s_%s&js=([(x)])&token=7bc05d0d4c3c22ef9fca8c2a912d779c"%(unknow_timestamp,str(time_tick_beijin))
    hexun_url = 'http://quote.forex.hexun.com/ForexXML/QTMI_CUR3/QTMI_CUR3_5_xagusd.xml?0.8608891293406487&ts=1511505692039'
    r = requests.get(hexun_url)
    print r.text
    info_content = r.text.split('(')[1].split(')')[0]
    #print info_content
    #print (info_content.split('%"'))
    for item in (info_content.split('%"')):
        #print (item)
        if item.find('XAG') != -1:
            #print item.split(',')
            ret_price = item.split(',')[4]
            break
    return [ret_price,ret_timestamp]

def home_dir():
    print sys.path
    print os.getcwd()
    print os.environ['HOME']
    print os.path.expandvars('$HOME')
    print os.path.expanduser('~')
    print __file__
    print os.path.abspath(os.getcwd()+os.path.sep+"..")

def update_serdb():
    file = 'F:\\code\\python\\RESTART\\core\\2018\\2018-04\\15min\\15min-ser.db'
    db = sqlite3.connect(file)
    dbCursor = db.cursor()
    item = ('2017/12/30  5:59:59',16,'15min','CDL3INSIDE',100,'',\
            17.19,'2017/12/30  4:59:59',17.09,'2017/12/30  4:59:59',\
            0,'',10000,'',0,'',10000,'',0,'',10000,'',0,'',10000,'',0,'',10000,'',0,'',10000,'',\
            1,1500)
    strtmp = '2018-01-11 12:45:30'
    try:
        #dbCursor.execute("update stratearnrate set time=? where indx=11",item)
        dbCursor.execute('update stratearnrate set \
        time=?,price=?,tmName=?,patternName=?,patternVal=?,DeadTime=?,\
        M15maxEarn=?,M15maxEarnTime=?,M15maxLoss=?,M15maxLossTime=?,\
        M30maxEarn=?,M30maxEarnTime=?,M30maxLoss=?,M30maxLossTime=?,\
        H1maxEarn=?,H1maxEarnTime=?,H1maxLoss=?,H1maxLossTime=?,\
        H2maxEarn=?,H2maxEarnTime=?,H2maxLoss=?,H2maxLossTime=?,\
        H4maxEarn=?,H4maxEarnTime=?,H4maxLoss=?,H4maxLossTime=?,\
        H6maxEarn=?,H6maxEarnTime=?,H6maxLoss=?,H6maxLossTime=?,\
        H12maxEarn=?,H12maxEarnTime=?,H12maxLoss=?,H12maxLossTime=?,\
        tmChainIndx=?,restCnt=? where indx = 1', item)
    except (Exception),e:
        print("update in stratearnrate db Exception: "+e.message)
    db.commit()
    dbCursor.close()
    db.close()

def practice_jinten():
    #声明一个CookieJar对象来保存cookie
    #req = urllib2.Request("https://www.jin10.com/price_wall/index.html")
    #response = urllib2.urlopen(req)
    #response=urllib2.urlopen('https://www.jin10.com/price_wall/index.html')
    #html=response.read()
    #print html
    #url = 'https://www.baidu.com'
    #values = {'name' : 'who','password':'123456'}
    #url = 'http://quote.eastmoney.com/globalfuture/SI00Y.html'
    time_now_tick = time.time()*1000
    url = 'http://hq.sinajs.cn/?_=%s/&list=hf_XAG'%str(time_now_tick)
    print url
    get_headers = {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Host':'hq.sinajs.cn',
    'If-None-Match':'W/"ICiAA1aWG7F"',
    'Referer':'http://finance.sina.com.cn/futures/quotes/XAG.shtml',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    }
    head={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'}
    #get_headers = {
    #'Connection' : 'keep-alive' ,
    #'Cache-Control' : 'max-age=0',
    #'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
    #'Accept-Language' : 'zh-CN,zh;q=0.8,en;q=0.6',
    #}
    req = requests.get(url, headers=head)
    print req
    req = urllib2.Request(url, None, head)
    print req
    response = urllib2.urlopen(req)
    the_page = response.read()
    response_url=response.geturl()
    info=response.info()
    code=response.getcode()
    print the_page
    print "==="
    print response_url,info,code

def dos_cmd_test():
    #subprocess.check_output('wget http://192.168.10.81/git/backup-git-warehouse.sh -P F:',shell=True)
    #os.system('dir')
    try:
        #urllib.urlretrieve('http://192.168.10.81/Start-V061/2017-52/15min.db',filename='F:\\15min.db')
        data = urllib2.urlopen('http://192.168.10.81/Fx678-V093AQ/2018/2018-02/')
        print data
    except Exception,e:
        print e

def box_show_test():
    root = Tkinter.Tk()
    #b = Tkinter.Button(root, text="关于", command=tkMessageBox.showinfo(title='aaa', message='bbb'))
    #b.pack()
    root.mainloop()

def email_send_test():
    '''发送电子邮件'''
    MAIL_FROM='liuruhengwilliam@sina.com'
    MAIL_TO = ['liuruhengwilliam@sina.com','joeeheng@sina.com']
    msg = MIMEText('Python email send practice',"plain",_charset='utf-8')
    msg['Subject'] = Header('email auto send','utf-8')
    msg["From"]=MAIL_FROM
    msg['Date']='2018-01-24'
    try:
        smtp = smtplib.SMTP()
        smtp.connect("smtp.sina.com",25)#SMTP端口号默认为25
        smtp.login("liuruhengwilliam", "Joe19800116")#用户名和密码
        smtp.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())
        print "True"
    except Exception as e:
        print e.message

def email_withattachment_send_test():
    '''发送电子邮件'''
    MAIL_FROM='liuruhengwilliam@sina.com'
    MAIL_TO = ['liuruhengwilliam@sina.com']#多人接收时可在该列表中添加
    #msg['To'] = ";".join(receiver)
    msg = MIMEMultipart()
    msg['Subject'] = Header('Email AutoMatic Send','utf-8')
    msg["From"]=MAIL_FROM
    msg['Date']='2018-01-24 16:00'
    msg.attach(MIMEText('Python email send practice',"plain",_charset='utf-8'))
    att1 = MIMEText(open('1hour-Jan20_20_18.png','rb').read(),'base64','utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    att1["Content-Disposition"] = 'attachment; filename="1hour-Jan20_20_18.png"'
    msg.attach(att1)
    try:
        smtp = smtplib.SMTP()
        smtp.connect("smtp.sina.com",25)#SMTP端口号默认为25
        smtp.login("liuruhengwilliam", "Joe19800116")#用户名和密码
        smtp.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())
        print "True"
    except Exception as e:
        print e.message
    smtp.quit()

def get_week_of_month(year, month, day):
     """
     获取指定的某天是某个月中的第几周
    周一作为一周的开始
    """
     end = int(datetime.datetime(year, month, day).strftime("%W"))
     begin = int(datetime.datetime(year, month, 1).strftime("%W"))
     return end - begin + 1

def upate_afterwards_KLine_indicator():
    """ 内部接口API：从策略盈亏率数据库中提取K线组合模式的指标值并更新相应实例。
                   事后统计--依次截取数据库中每个条目。
    """
    # 清空摘要说明
    #self.summaryDict['KLine']=''
    # 策略盈亏率数据精加工
    serData = {}
    for period in Constant.QUOTATION_DB_PREFIX[2:3]:#前闭后开  暂时只考虑15min/30min/1hour
        filename = Configuration.get_period_working_folder(period)+period+'-ser.db'
        tempDf = Primitive.translate_db_to_df(filename)
        # 填充字典。结构为"周期:DataFrame"
        #serData.update({period:tempDf})
        # 填充"区间格"。为后续计算多周期策略重叠区域做准备。
        #print tempDf.iloc[0][Constant.SER_DF_STRUCTURE.index('time')]
        prePolicyTime = ''
        for itemRow in tempDf.itertuples():
            time = itemRow[Constant.SER_DF_STRUCTURE.index('time')+1]
            if time == prePolicyTime:
                continue
            else:
                prePolicyTime = time

            dfIndicator = tempDf[tempDf['time'] == time]
            print dfIndicator
            #for onePoint in dfIndicator.itertuples():
            #    tempDf.drop(onePoint[Constant.SER_DF_STRUCTURE.index('indx')+1]-1,inplace=True)
            #print tempDf
            #print time.split(' ')[0],type(time.split(' ')[0])
            #current = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
            #weekday,hour,minute = int(current.isoweekday()),int(current.strftime("%H")),int(current.strftime("%M"))
            #print weekday,hour,minute


if __name__ == '__main__':
    csv_test()
    #db_test()
    #file_test()
    #talib_func()
    #talib_macd()
    #talib_sma_test()
    #query_info()
    #get_property()
    #db_test()
    #home_dir()
    #datetime_test()
    #talib_pattern_15min()
    #sma_test()
    #update_serdb()
    #practice_jinten()
    #dos_cmd_test()
    #create_db_test()
    #insert_db_test()
    #update_db_test()
    #box_show_test()
    #email_send_test()
    #email_withattachment_send_test()
    #print get_week_of_month(2018,2,28)
    #for item in os.listdir('F:\\code\\python\\RESTART\\core\\2018\\2018-09\\15min'):
    #    if item.find('.png') != -1:
    #        print item
    #        os.remove('F:\\code\\python\\RESTART\\core\\2018\\2018-09\\15min\%s'%item)
    #upate_afterwards_KLine_indicator()
    sys.exit()
