#coding=utf-8

import wx
import platform
import sys
import os
import pandas as pd
#from resource import Constant
#from resource import Configuration
#from resource import DataSettleKit
#from indicator import CandleStick
#from strategy.ClientMatch import ClientMatch
#from strategy.Strategy import Strategy

class DirDialog(wx.Frame):
    """"""
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self,None,-1,u"文件夹选择对话框")
        b = wx.Button(self,-1,u"文件夹选择对话框")
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)

    #----------------------------------------------------------------------
    def OnButton(self, event):
        """"""
        dlg = wx.DirDialog(self,u"选择文件夹",style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            print dlg.GetPath() #文件夹路径

        dlg.Destroy()

if __name__ == '__main__':
    frame = wx.PySimpleApp()
    app = DirDialog()
    app.Show()
    frame.MainLoop()

"""
    辅助类：
    1.画图方法；
    2.历史数据分析；
"""

def old_API():
    choiceIndex = raw_input("Please choose:\n"+"  1.drawing picture of indicator\n"\
                            +"  2.analyse quote data in history\n"\
                            +"  3.translate quote database to csv file\n"\
                            +"Your choice:\n")
    if choiceIndex == '1':
        filename = raw_input("file name input: ")
        periodName = raw_input("period name input:")
        if Constant.QUOTATION_DB_PREFIX.count(periodName) == 0:
            print "Error period name!"
            sys.exit()
        if filename.find('.csv') != -1:
            target=Configuration.get_field_from_string(filename)[-1].split('-')[0]
            data = pd.read_csv(filename)
            data = data.iloc[len(Constant.QUOTATION_DB_PERIOD):]
            CandleStick.manual_show_candlestick(target,periodName,data[data['period']==periodName])
        else:
            print "Error file name input!"
    elif choiceIndex == '2':
        path = raw_input("Please input folder path WITH THE END OF '\\': ")
        if path=='':
            path = Configuration.get_working_directory()
        clientMatchHdl = ClientMatch(path)
        clientMatchHdl.match_KLineIndicator()
    elif choiceIndex == '3':
        filePath = raw_input("Please input full path of database file: ")
        ret = DataSettleKit.translate_db_into_csv(filePath)
        if ret == False:
            print "Failed to translate file:%s"%filePath
        else:
            print "Completed Successfully!"
    else:
        print "Error choice!"
