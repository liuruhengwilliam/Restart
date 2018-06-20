# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class ToolsFrame
###########################################################################

class ToolsFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"工具软件", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

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
        print event
        event.Skip()

    def m_menuItem_exitOnMenuSelection( self, event ):
        print event
        event.Skip()

    def m_menuItem_aboutOnMenuSelection( self, event ):
        print event
        event.Skip()

    def m_filePickerOnFileChanged( self, event ):
        print self.m_filePicker.GetPath()
        event.Skip()

    def m_comboBox_typeOnCombobox( self, event ):
        print self.m_comboBox_type.GetSelection()
        event.Skip()

    def m_button_okOnButtonClick( self, event ):
        print event
        event.Skip()

class AssistantKit(ToolsFrame):
    def kit_init(self):
        pass

if __name__ == '__main__':
    app = wx.App(False)
    frame = AssistantKit(None)
    frame.kit_init()
    frame.Show()
    app.MainLoop()

