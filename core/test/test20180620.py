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
## Class AssistantFrame
###########################################################################

class AssistantFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,296 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Please choose the db file:", wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		self.m_staticText1.Wrap( -1 )
		self.m_staticText1.SetFont( wx.Font( 16, 70, 90, 90, False, "宋体" ) )

		bSizer1.Add( self.m_staticText1, 0, wx.ALL, 5 )

		self.m_dbfile_textCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,20 ), 0 )
		bSizer1.Add( self.m_dbfile_textCtrl, 0, wx.ALL, 5 )

		self.m_dbfile_button = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.m_dbfile_button, 0, wx.ALL, 5 )
		self.Bind(wx.EVT_BUTTON, self.OnClick, self.m_dbfile_button)

		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

	def OnClick(self,event):
		self.m_dbfile_button.SetLabel("Clicked")
		print "clicked"

	def __del__( self ):
		pass

class TestWindows(AssistantFrame):
    def init_test(self):
        self.m_dbfile_textCtrl.SetValue("Test")
    #def main_button_click(self):
    #    self.m_dbfile_textCtrl.SetValue("done")

if __name__ == "__main__":
    app = wx.App()
    frame = TestWindows(None)
    frame.init_test()
    frame.Show()
    app.MainLoop()
