# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################
FRAME_TOOLS = 0#GUI主窗体框架
FRAME_ABOUT = 1#About窗体框架
FRAME_INFO = 2#提示信息窗体框架。
FRAME_USAGE = 3#提示信息窗体框架。

import os
import wx
import pandas as pd
from resource import Constant
from resource import Configuration
from resource import DataSettleKit
from indicator import CandleStick
from statistics.Statistics import Statistics

###########################################################################
## Class AboutFrame
###########################################################################
class AboutFrame ( wx.Frame ):
    """ About窗体框架。拷贝自wyFormBuilder工程 """
    def __init__( self, parent, id=-1, UpdateUI=None ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"修改记录", pos = wx.DefaultPosition,\
                            size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.UpdateUI = UpdateUI
        sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY ), wx.VERTICAL )

        self.m_staticText_about = wx.StaticText( sbSizer.GetStaticBox(), wx.ID_ANY, \
                u"V0.0.1  创建工程和Demo  Date: 2018-06-20\nV0.0.2  布局调整和相关按键事件处理  Date: 2018-06-29",\
                wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_about.Wrap( -1 )
        sbSizer.Add( self.m_staticText_about, 0, wx.ALL, 5 )

        self.SetSizer( sbSizer )
        self.Layout()

        self.Centre( wx.BOTH )
        # Connect Events
        self.Bind( wx.EVT_CLOSE, self.AboutFrameOnClose )

    # Virtual event handlers, overide them in your derived class
    def AboutFrameOnClose( self, event ):
        """ 捕捉窗体框架的关闭事件，切换到程序主窗体框架。 """
        self.UpdateUI(FRAME_TOOLS)
        event.Skip()

    def __del__( self ):
        pass

###########################################################################
## Class UsageFrame
###########################################################################
class UsageFrame ( wx.Frame ):
    """ Usage窗体框架。拷贝自wyFormBuilder工程 """
    def __init__( self, parent, id=-1, UpdateUI=None ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"使用说明", pos = wx.DefaultPosition,\
                            size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.UpdateUI = UpdateUI
        sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY ), wx.VERTICAL )

        self.m_staticText_usage = wx.StaticText( sbSizer.GetStaticBox(), wx.ID_ANY, \
                u"1.通过本软件生成的文件保存在所选择的文件目录中；\n2.只有在绘制蜡烛图等指标文件时才需要选择周期；",\
                wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_usage.Wrap( -1 )
        sbSizer.Add( self.m_staticText_usage, 0, wx.ALL, 5 )

        self.SetSizer( sbSizer )
        self.Layout()

        self.Centre( wx.BOTH )
        # Connect Events
        self.Bind( wx.EVT_CLOSE, self.UsageFrameOnClose )

    # Virtual event handlers, overide them in your derived class
    def UsageFrameOnClose( self, event ):
        """ 捕捉窗体框架的关闭事件，切换到程序主窗体框架。 """
        self.UpdateUI(FRAME_TOOLS)
        event.Skip()

    def __del__( self ):
        pass

###########################################################################
## Class InfoFrame
###########################################################################
class InfoFrame ( wx.Frame ):
    """ 提示信息窗体框架。拷贝自wyFormBuilder工程 """
    def __init__( self, parent, id=-1, UpdateUI=None, info=None ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"提示信息", pos = wx.DefaultPosition,\
                            size = wx.Size( 322,141 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.UpdateUI = UpdateUI
        sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY ), wx.VERTICAL )

        self.m_staticText_info = wx.StaticText( sbSizer.GetStaticBox(), wx.ID_ANY, info, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_info.Wrap( -1 )
        sbSizer.Add( self.m_staticText_info, 0, wx.ALL, 5 )

        self.SetSizer( sbSizer )
        self.Layout()

        self.Centre( wx.BOTH )
        # Connect Events
        self.Bind( wx.EVT_CLOSE, self.InfoFrameOnClose )

    # Virtual event handlers, overide them in your derived class
    def InfoFrameOnClose( self, event ):
        """ 捕捉窗体框架的关闭事件，切换到程序主窗体框架。 """
        self.UpdateUI(FRAME_TOOLS)
        event.Skip()

    def __del__( self ):
        pass

###########################################################################
## Class ToolsFrame
###########################################################################
class ToolsFrame ( wx.Frame ):
    """ 程序主窗体框架。拷贝自wyFormBuilder工程 """
    def __init__( self, parent, id=-1, UpdateUI=None ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"工具软件", pos = wx.DefaultPosition,\
                            size = wx.Size( 527,212 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.UpdateUI = UpdateUI
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        self.m_menubar = wx.MenuBar( 0 )
        self.m_menu_file = wx.Menu()
        self.m_menuItem_usage = wx.MenuItem( self.m_menu_file, wx.ID_ANY, u"使用说明", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu_file.AppendItem( self.m_menuItem_usage )

        self.m_menu_file.AppendSeparator()

        self.m_menuItem_exit = wx.MenuItem( self.m_menu_file, wx.ID_ANY, u"退出", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu_file.AppendItem( self.m_menuItem_exit )

        self.m_menubar.Append( self.m_menu_file, u"操作" )

        self.m_menu_help = wx.Menu()
        self.m_menuItem_about = wx.MenuItem( self.m_menu_help, wx.ID_ANY, u"关于软件", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu_help.AppendItem( self.m_menuItem_about )

        self.m_menubar.Append( self.m_menu_help, u"帮助" )

        self.SetMenuBar( self.m_menubar )

        fgSizer_main = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer_main.SetFlexibleDirection( wx.BOTH )
        fgSizer_main.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText_type = wx.StaticText( self, wx.ID_ANY, u"操作类型", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_type.Wrap( -1 )
        fgSizer_main.Add( self.m_staticText_type, 0, wx.ALL, 5 )

        m_comboBox_typeChoices = [u"1.db文件转换成csv文件",u"2.csv行情文件中的数据排序及去重",u"3.csv行情文件中的数据绘制蜡烛图等指标并存档",u"4.csv盈亏文件中的数据分析及统计"]
        self.m_comboBox_type = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 400,-1 ), m_comboBox_typeChoices, 0 )
        self.m_comboBox_type.SetFont( wx.Font( 12, 70, 90, 90, False, "宋体" ) )

        fgSizer_main.Add( self.m_comboBox_type, 0, wx.ALL, 5 )

        self.m_staticText_file = wx.StaticText( self, wx.ID_ANY, u"文件选择", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_file.Wrap( -1 )
        fgSizer_main.Add( self.m_staticText_file, 0, wx.ALL, 5 )

        self.m_filePicker = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"选择文件", u"*.*", wx.DefaultPosition, wx.Size( 400,-1 ), wx.FLP_DEFAULT_STYLE|wx.FLP_SMALL )
        fgSizer_main.Add( self.m_filePicker, 0, wx.ALL, 5 )

        self.m_staticText_period = wx.StaticText( self, wx.ID_ANY, u"周期（可选）", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_period.Wrap( -1 )
        fgSizer_main.Add( self.m_staticText_period, 0, wx.ALL, 5 )

        m_choice_periodChoices = [u"5分钟", u"12小时", u"1天", u"1周", u"15分钟", u"30分钟", u"1小时", u"2小时", u"4小时", u"6小时" ]
        self.m_choice_period = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice_periodChoices, 0 )
        self.m_choice_period.SetSelection( 0 )
        fgSizer_main.Add( self.m_choice_period, 0, wx.ALL, 5 )

        self.m_button_done = wx.Button( self, wx.ID_ANY, u"确定", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer_main.Add( self.m_button_done, 0, wx.ALL, 5 )

        self.SetSizer( fgSizer_main )
        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_MENU, self.m_menuItem_usageOnMenuSelection, id = self.m_menuItem_usage.GetId() )
        self.Bind( wx.EVT_MENU, self.m_menuItem_exitOnMenuSelection, id = self.m_menuItem_exit.GetId() )
        self.Bind( wx.EVT_MENU, self.m_menuItem_aboutOnMenuSelection, id = self.m_menuItem_about.GetId() )
        self.m_filePicker.Bind( wx.EVT_FILEPICKER_CHANGED, self.m_filePickerOnFileChanged )
        self.m_comboBox_type.Bind( wx.EVT_COMBOBOX, self.m_comboBox_typeOnCombobox )
        self.m_choice_period.Bind( wx.EVT_CHOICE, self.m_choice_periodOnChoice )
        self.m_button_done.Bind( wx.EVT_BUTTON, self.m_button_doneOnButtonClick )

        self.filePath = ''#文件路径
        self.operationType = -1#操作类型
        self.period = 0#周期序号

    def __del__( self ):
        pass

    # Virtual event handlers, overide them in your derived class
    def m_menuItem_usageOnMenuSelection( self, event ):
        """ Open事件处理回调 """
        self.UpdateUI(FRAME_USAGE)
        event.Skip()

    def m_menuItem_exitOnMenuSelection( self, event ):
        """ Exit事件处理回调 """
        event.Skip()
        os._exit(0)

    def m_menuItem_aboutOnMenuSelection( self, event ):
        """ About事件处理回调。启动About窗体框架 """
        self.UpdateUI(FRAME_ABOUT)
        event.Skip()

    def m_filePickerOnFileChanged( self, event ):
        """ 文件挑选控件的事件回调 """
        self.filePath = self.m_filePicker.GetPath()
        event.Skip()

    def m_comboBox_typeOnCombobox( self, event ):
        """ 事件处理类型下拉框的回调 """
        self.operationType = self.m_comboBox_type.GetSelection()
        event.Skip()

    def m_choice_periodOnChoice( self, event ):
        self.period = self.m_choice_period.GetSelection()
        event.Skip()

    def m_button_doneOnButtonClick( self, event ):
        """ OK按键事件的回调 """
        self.OperateAssistant()
        event.Skip()

    def OperateAssistant(self):
        """ 具体事务的处理函数 """
        if self.filePath=='':
            self.UpdateUI(FRAME_INFO,u"未选择文件")
            return

        if self.filePath.find('.db')==-1 and self.filePath.find('-quote.csv')==-1 and self.filePath.find('Properties.xml')==-1:
            self.UpdateUI(FRAME_INFO,u"所选择的文件类型不匹配")
            return
        # 相关目录路径
        path = self.filePath.strip(Configuration.get_field_from_string(self.filePath,'\\')[-1])

        if self.operationType == 0:#translate db to csv file
            DataSettleKit.translate_db_into_csv(self.filePath)
        elif self.operationType == 1:#draw candlestick with quote file
            target = Configuration.get_field_from_string(self.filePath,'\\')[-1].split('-')[0]
            data = pd.read_csv(self.filePath)
            data = data.iloc[len(Constant.QUOTATION_DB_PERIOD):]
            periodName = Constant.QUOTATION_DB_PREFIX[self.period]
            CandleStick.manual_show_candlestick(target,periodName,data[data['period']==periodName],path)
        elif self.operationType == 2:#analyse strategy with ser file defined in Properties.xml
            clientMatchHdl = Statistics(path)
            clientMatchHdl.match_KLineIndicator()
        else:#should be popup toast of ERROR
            self.UpdateUI(FRAME_INFO,u"未选择操作类型")

class GuiManager():
    """ 窗体管理(切换)类 """
    def __init__(self, UpdateUI):
        self.UpdateUI = UpdateUI
        self.frameDict = {} # 用来装载已经创建的Frame对象

    def GetFrame(self, type,info=None):
        """ 外部接口API """
        frame = self.frameDict.get(type)
        if frame is None:
            frame = self.CreateFrame(type,info)
            self.frameDict[type] = frame
        return frame

    def ClearFrame(self, type):
        """ 外部接口API """
        self.frameDict[type] = None

    def CreateFrame(self, type, info=None):
        if type == FRAME_TOOLS:
            return ToolsFrame(parent=None, id=type, UpdateUI=self.UpdateUI)
        elif type == FRAME_ABOUT:
            return AboutFrame(parent=None, id=type, UpdateUI=self.UpdateUI)
        elif type == FRAME_USAGE:
            return UsageFrame(parent=None, id=type, UpdateUI=self.UpdateUI)
        elif type == FRAME_INFO:
            return InfoFrame(parent=None, id=type, UpdateUI=self.UpdateUI, info=info)

class AssistantGUI(wx.App):
    def OnInit(self):
        self.manager = GuiManager(self.UpdateUI)
        self.frame = self.manager.GetFrame(FRAME_TOOLS)
        self.frame.Show()
        return True

    def UpdateUI(self, type, info=None):
        self.frame.Show(False)
        if type != FRAME_TOOLS:#非程序主窗体框架需要清除
            self.manager.ClearFrame(type)
        self.frame = self.manager.GetFrame(type,info)
        self.frame.Show(True)

if __name__ == '__main__':
    app = AssistantGUI()
    app.MainLoop()
