#coding=utf-8

class engineException(Exception):
    """数据引擎模块自定义异常"""
    def __init__(self,err='engine Exception'):
        Exception.__init__(self,err)