#coding=utf-8

import Constant
import Trace
import platform
import sys
import os

def misc_init():
    """初始化资源模块的相关内容"""
    Trace.output('info',Constant.get_version_info())
    
    if (platform.system() == "Linux"):
        sys.path.append(os.getcwd()+'/quotation')
        sys.path.append(os.getcwd()+'/resource')
        sys.path.append(os.getcwd()+'/engine') 
        sys.path.append(os.getcwd()+'/timer')
