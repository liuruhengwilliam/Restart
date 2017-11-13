#coding=utf-8

from core.resource import Configuration
from core.quotation import QuotationKit

def db_to_csv(file,cnt):
    """ db文件转换成csv文件的工具函数
        file: db文件名（含文件路径）。raw_input方式接收控制台输入，字符串类型。
        cnt: 带转换db条目的行数。raw_input方式接收控制台输入，字符串类型，且-1为全部转换。
    """
    fileName = ''
    if len(file) < 10: # 不含文件路径的简约情况下，默认路径是当周文件夹路径
        fileName = Configuration.get_working_directory()+'/'+file
    else:
        fileName = file

    QuotationKit.translate_db_into_csv(fileName,int(cnt))

if __name__ == '__main__':
    filename = raw_input("file name input: ")
    cnt = raw_input("cnt to be translated: ")
    db_to_csv(filename,cnt)