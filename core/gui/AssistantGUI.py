# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################
FRAME_TOOLS = 0#GUI主窗体框架
FRAME_ABOUT = 1#About窗体框架
FRAME_OPEN = 2#Open窗体框架。待实现。

import wx
import wx.xrc
###########################################################################
## Class AboutFrame
###########################################################################
class AboutFrame ( wx.Frame ):
    """ About窗体框架。拷贝自wyFormBuilder工程 """
    def __init__( self, parent, id=-1, UpdateUI=None ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.UpdateUI = UpdateUI
        sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"about the software" ), wx.VERTICAL )

        self.m_staticText_about = wx.StaticText( sbSizer.GetStaticBox(), wx.ID_ANY, u"show the method to use this software.", wx.DefaultPosition, wx.DefaultSize, 0 )
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
## Class ToolsFrame
###########################################################################

class ToolsFrame ( wx.Frame ):
    """ 程序主窗体框架。拷贝自wyFormBuilder工程 """
    def __init__( self, parent, id=-1, UpdateUI=None ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"工具软件", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.UpdateUI = UpdateUI
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        self.m_menubar = wx.MenuBar( 0 )
        self.m_menu_file = wx.Menu()
        self.m_menuItem_open = wx.MenuItem( self.m_menu_file, wx.ID_ANY, u"Open", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu_file.AppendItem( self.m_menuItem_open )

        self.m_menu_file.AppendSeparator()

        self.m_menuItem_exit = wx.MenuItem( self.m_menu_file, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu_file.AppendItem( self.m_menuItem_exit )

        self.m_menubar.Append( self.m_menu_file, u"File" )

        self.m_menu_help = wx.Menu()
        self.m_menuItem_about = wx.MenuItem( self.m_menu_help, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu_help.AppendItem( self.m_menuItem_about )

        self.m_menubar.Append( self.m_menu_help, u"Help" )

        self.SetMenuBar( self.m_menubar )

        bSizer_operation = wx.BoxSizer( wx.VERTICAL )

        self.m_filePicker = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*", wx.DefaultPosition, wx.Size( 500,-1 ), wx.FLP_DEFAULT_STYLE|wx.FLP_SMALL )
        bSizer_operation.Add( self.m_filePicker, 0, wx.ALL, 5 )

        gSizer = wx.GridSizer( 0, 2, 0, 0 )

        m_comboBox_typeChoices = [ u"1. translate db to csv file", u"2. draw candlestick with quote file", u"3. analyse strategy with csv file" ]
        self.m_comboBox_type = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), m_comboBox_typeChoices, 0 )
        self.m_comboBox_type.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )

        gSizer.Add( self.m_comboBox_type, 0, wx.ALL, 5 )

        self.m_button_ok = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer.Add( self.m_button_ok, 0, wx.ALL, 5 )

        bSizer_operation.Add( gSizer, 1, wx.EXPAND, 5 )

        self.SetSizer( bSizer_operation )
        self.Layout()
        bSizer_operation.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_MENU, self.m_menuItem_openOnMenuSelection, id = self.m_menuItem_open.GetId() )
        self.Bind( wx.EVT_MENU, self.m_menuItem_exitOnMenuSelection, id = self.m_menuItem_exit.GetId() )
        self.Bind( wx.EVT_MENU, self.m_menuItem_aboutOnMenuSelection, id = self.m_menuItem_about.GetId() )
        self.m_filePicker.Bind( wx.EVT_FILEPICKER_CHANGED, self.m_filePickerOnFileChanged )
        self.m_comboBox_type.Bind( wx.EVT_COMBOBOX, self.m_comboBox_typeOnCombobox )
        self.m_button_ok.Bind( wx.EVT_BUTTON, self.m_button_okOnButtonClick )

    def __del__( self ):
        pass

    # Virtual event handlers, overide them in your derived class
    def m_menuItem_openOnMenuSelection( self, event ):
        """ Open事件处理回调 """
        event.Skip()

    def m_menuItem_exitOnMenuSelection( self, event ):
        """ Exit事件处理回调 """
        event.Skip()

    def m_menuItem_aboutOnMenuSelection( self, event ):
        """ About事件处理回调。启动About窗体框架 """
        self.UpdateUI(FRAME_ABOUT)
        event.Skip()

    def m_filePickerOnFileChanged( self, event ):
        """ 文件挑选控件的事件回调 """
        print self.m_filePicker.GetPath()
        event.Skip()

    def m_comboBox_typeOnCombobox( self, event ):
        """ 事件处理类型下拉框的回调 """
        print self.m_comboBox_type.GetSelection()
        event.Skip()

    def m_button_okOnButtonClick( self, event ):
        """ OK按键事件的回调 """
        event.Skip()

class GuiManager():
    """ 窗体管理(切换)类 """
    def __init__(self, UpdateUI):
        self.UpdateUI = UpdateUI
        self.frameDict = {} # 用来装载已经创建的Frame对象

    def GetFrame(self, type):
        """ 外部接口API """
        frame = self.frameDict.get(type)
        if frame is None:
            frame = self.CreateFrame(type)
            self.frameDict[type] = frame
        return frame

    def ClearFrame(self, type):
        """ 外部接口API """
        self.frameDict[type] = None

    def CreateFrame(self, type):
        if type == FRAME_TOOLS:
            return ToolsFrame(parent=None, id=type, UpdateUI=self.UpdateUI)
        elif type == FRAME_ABOUT:
            return AboutFrame(parent=None, id=type, UpdateUI=self.UpdateUI)

class AssistantKit(wx.App):
    def OnInit(self):
        self.manager = GuiManager(self.UpdateUI)
        self.frame = self.manager.GetFrame(FRAME_TOOLS)
        self.frame.Show()
        return True

    def UpdateUI(self, type):
        self.frame.Show(False)
        if type != FRAME_TOOLS:#非程序主窗体框架需要清除
            self.manager.ClearFrame(type)
        self.frame = self.manager.GetFrame(type)
        self.frame.Show(True)

if __name__ == '__main__':
    app = AssistantKit()
    app.MainLoop()
