#coding=utf-8

import os
import zipfile
import urllib
import datetime
import platform
import threading
import tkMessageBox
import Tkinter
import xml.etree.ElementTree as ET
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import Trace
import Constant

def get_field_from_string(str,separator=None):
    """ 内外部接口API: 获取字符串中某分隔符下的字段
        返回列值：列表
        str: 待分解的字符串
        separator: 分隔符的定义。默认分解文件路径字符串。
    """
    sysName = platform.system()
    if (sysName == "Windows"):
        if separator == None:
            retList = str.split('\\')
        else:
            retList = str.split(separator)
    elif (sysName == "Linux"):
        if separator == None:
            retList = str.split('/')
    else :# 未知操作系统
        retList = []
    return retList

def create_working_directory():
    """ 内/外部接口API：获取当前周工作目录
        返回值:工作目录字符串
    """
    # 寻找当前周数并生成文件名前缀
    dt = datetime.datetime.now()
    year,week = dt.strftime('%Y'),dt.strftime('%U')
    fileNamePrefix = year+'-'+week

    #生成文件路径(依据不同操作系统)
    sysName = platform.system()
    if (sysName == "Windows"):
        dirPath = os.getcwd()+'\\'+year+'\\'+fileNamePrefix+'\\'
    elif (sysName == "Linux"):
        dirPath = os.getcwd()+'/'+year+'/'+fileNamePrefix+'/'
    else :# 未知操作系统
        dirPath = fileNamePrefix

    if not os.path.exists(dirPath):
        # 创建当周数据库文件夹
        os.makedirs(dirPath)

def get_current_directory():
    """内/外部接口API：获取当前目录"""
    #生成文件路径(依据不同操作系统)
    sysName = platform.system()
    if (sysName == "Windows"):
        dirPath = os.getcwd()+'\\'
    elif (sysName == "Linux"):
        dirPath = os.getcwd()+'/'
    else :# 未知操作系统
        dirPath = ''
    return dirPath

def get_working_directory():
    """内/外部接口API：获取当前周工作目录"""
    dt = datetime.datetime.now()
    year,week = dt.strftime('%Y'),dt.strftime('%U')
    fileNamePrefix = year+'-'+week

    #生成文件路径(依据不同操作系统)
    sysName = platform.system()
    if (sysName == "Windows"):
        dirPath = os.getcwd()+'\\'+year+'\\'+fileNamePrefix+'\\'
    elif (sysName == "Linux"):
        dirPath = os.getcwd()+'/'+year+'/'+fileNamePrefix+'/'
    else :# 未知操作系统
        dirPath = fileNamePrefix

    # 避免嵌套调用，不能调用get_property()
    if not os.path.exists(dirPath+'Properties.xml'):
        return dirPath
    # 寻找配置文件中的相关项
    try:
        tree = ET.parse(dirPath+'Properties.xml')
        root = tree.getroot()
    except Exception,e:
        return dirPath
    for item in root.findall('workfolder'):
        dirPath = item.find('value').text
    return dirPath

def get_back_week_directory(path,backDeepCnt):
    """ 外部接口API：搜索前若干周的路径
        backDeepCnt: 追溯的历史周数
        path: 当前目录（含有周期字符串）
    """
    sysName = platform.system()
    if (sysName == "Windows"):
        year,week = path.split('\\')[-2].split('-')
        if int(week)-backDeepCnt <= 0:
            dirPath = os.getcwd()+'\\'+str(int(year)-1)+'\\'+\
                      '%s-%s'%(str(int(year)-1),str(52+int(week)-backDeepCnt))+'\\'
        else:
            dirPath = os.getcwd()+'\\'+year+'\\'+'%s-%s'%(year,str(int(week)-backDeepCnt))+'\\'
    elif (sysName == "Linux"):
        year,week = path.split('/')[-2].split('-')
        if int(week)-backDeepCnt <= 0:
            dirPath = os.getcwd()+'/'+str(int(year)-1)+'/'+\
                      '%s-%s'%(str(int(year)-1),str(52+int(week)-backDeepCnt))+'/'
        else:
            dirPath = os.getcwd()+'/'+year+'/'+'%s-%s'%(year,str(int(week)-backDeepCnt))+'/'
    else :# 未知操作系统
        dirPath = get_working_directory()

    return dirPath

# 对于程序运行过程中的调试和异常等情况，需要通过XML配置文件加载相关属性方式调整流程，便于分析问题。
def get_property(strProperty):
    """ 内/外部接口API：根据XML配置文件读取相关属性字段
        入参：strProperty 属性字符串
        返回值：若XML文件中存在对应属性，则返回属性值；否则返回None。
    """
    ret = None
    #服务端程序(Stock/Futures)调用
    fileName = get_working_directory()+'Properties.xml'
    if not os.path.exists(fileName):
        return None

    try:
        tree = ET.parse(fileName)
        root = tree.getroot()
    except Exception,e:
        Trace.output('fatal','get_property exception:'+e.message)
        return None

    for item in root.findall(strProperty):
        ret = item.find('value').text

    return ret

def parse_target_list(specialPath=None):
    """ 外部函数API：配置文件中标的列表的查询函数。标的可能是单一期货/大宗商品，也可能是股票代码列表。
        返回值：标的列表。
    """
    if specialPath is None:
        fileName = get_working_directory()+'Properties.xml'
    else:
        fileName = specialPath+'Properties.xml'
    if os.path.exists(fileName)==False:
        return None

    try:
        tree = ET.parse(fileName)
        root = tree.getroot()
    except Exception,e:
        Trace.output('fatal','get_property exception:'+e.message)
        return None
    ret = ['Silver']
    for item in root.findall('target'):
        ret = item.find('value').text
    if ret is not None:
        return ret.replace('\n','').replace('\t','').replace(' ','').split(';')
    else:
        return ret

def zip_data_statistics_file(zipName,path):
    """ 外部接口API:数据和分析文件打包函数
        zipName:打包文件名。
        path:打包文件的路径。
    """
    f = zipfile.ZipFile(zipName,'w',zipfile.ZIP_STORED)
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            f.write(os.path.join(dirpath,filename))
    f.close()

def exit_client():
    """外部接口API：客户端程序退出检测
        配置文件可设置。若未设定则默认退出。
    """
    exitClient = True
    exitClient = get_property('exitClient')
    return exitClient

#邮箱地址和登陆密码成对放置
DEFAULT_MAILBOX_INFO = 'liuruhengwilliam@sina.com;Joe19800116'
DEFAULT_MAILBOX_SMTP = 'smtp.sina.com'
def send_notification_email(title,text,attachment=None):
    """ 外部接口API：发送通知的电子邮件
        title: 邮件标题字符串
        text: 邮件正文字符串
        attachment：附件文件路径字符串的列表结构
    """
    #发件箱
    senderMailbox = get_property('senderMailbox')
    if senderMailbox == None:
        senderMailbox = DEFAULT_MAILBOX_INFO.split(';')[0]
    #发件箱密码
    pwdString = get_property('pwdMailbox')
    if pwdString == None:
        pwdString = DEFAULT_MAILBOX_INFO.split(';')[1]
    #发件箱代理
    smtpString = get_property('smtpMailbox')
    if smtpString == None:
        smtpString = DEFAULT_MAILBOX_SMTP

    #收件箱
    recipientString = get_property('recipientMailbox')
    if recipientString == None:
        recipientMailbox = [DEFAULT_MAILBOX_INFO.split(';')[0]]
    elif recipientString.find(';') != -1:#多收件箱的字符格式标记为以分号相隔
        recipientMailbox = recipientString.split(';')
    else:
        recipientMailbox = [recipientString]

    #邮件主体
    msg = MIMEMultipart()
    msg['Subject'] = Header(title,'utf-8')
    msg["From"] = senderMailbox
    msg['Date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    msg.attach(MIMEText(text,"plain",_charset='utf-8'))

    #邮件附件
    if attachment != None:
        for attach in attachment:
            att = MIMEText(open(attach,'rb').read(),'base64','utf-8')
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment;filename=%s'%attach
            msg.attach(att)

    try:
        smtp = smtplib.SMTP()
        smtp.connect(smtpString,25)#SMTP端口号默认为25
        smtp.login(senderMailbox.split('@')[0], pwdString)#用户名和密码
        smtp.sendmail(senderMailbox, recipientMailbox, msg.as_string())
    except Exception as e:
        print e.message
        Trace.output('fatal',"send Email Exception: " + e.message)
    finally:
        smtp.quit()

def show_notification_ondesktop(title,text):
    """ 外部接口API：桌面通知和弹框
        title: 邮件标题字符串
        text: 邮件正文字符串
        参考资料:https://www.cnblogs.com/hhh5460/p/6664021.html?utm_source=itdadao&utm_medium=referral
    """
    if platform.system() != 'Windows':
        return

    if get_property('popupNotification') == 'False':
        return
    root = Tkinter.Tk()
    time=Tkinter.Frame()
    time.pack(fill="x")
    direction=Tkinter.Frame()
    direction.pack(fill="x")
    body=Tkinter.Frame()
    body.pack(fill="x")

    Tkinter.Label(time,text='时间：', width=8).pack(side=Tkinter.LEFT)
    l1 = Tkinter.Label(time,text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), width=30,height=5)
    l1.pack(side=Tkinter.LEFT)
    Tkinter.Label(direction,text='方向：', width=8).pack(side=Tkinter.LEFT)
    l2 = Tkinter.Label(direction,text=title, width=30,height=5)
    l2.pack(side=Tkinter.LEFT)
    Tkinter.Label(body,text='详情：', width=8).pack(side=Tkinter.LEFT)
    l3 = Tkinter.Label(body,text=text, width=30,height=5)
    l3.pack(side=Tkinter.LEFT)

    root.mainloop()
