#coding=utf-8
import wx

class PageOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent,size=(240,250))
        self.panel = wx.Panel(self)
        self.button = wx.Button(self.panel, -1, "hello", pos=(1, 1))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        self.button.SetDefault()

    def OnClick(self,event):
        self.button.SetLabel("Clicked")
        print "clicked"

class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(840,450))
        self.panel = wx.Panel(self)

class PageThree(wx.Panel):
    def __init__(self, parent):
         wx.Panel.__init__(self, parent)
         panel = wx.Panel(self)
         colour = [(160,255,204),(153,204,255),(151,253,225),]
         self.SetBackgroundColour(colour[0])
         self.center = wx.StaticText(self, -1, "使用说明", (355, 35),
                (100, -1), wx.ALIGN_CENTER)
         font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
         self.center.SetFont(font)

class PageFour(wx.Panel):
    def __init__(self, parent):
         wx.Panel.__init__(self, parent)
         panel = wx.Panel(self)
         colour = [(160,255,204),(153,204,255),(151,253,225),]
         self.SetBackgroundColour(colour[0])
         self.center = wx.StaticText(self, -1, "使用说明", (355, 35),
                (100, -1), wx.ALIGN_CENTER)
         font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
         self.center.SetFont(font)

class PageFive(wx.Panel):
    def __init__(self, parent):
         wx.Panel.__init__(self, parent)
         panel = wx.Panel(self)
         colour = [(160,255,204),(153,204,255),(151,253,225),]
         self.SetBackgroundColour(colour[0])
         self.center = wx.StaticText(self, -1, "使用说明", (355, 35),
                (100, -1), wx.ALIGN_CENTER)
         font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
         self.center.SetFont(font)

if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None, title="工具软件V2.2.1")
    nb = wx.Notebook(frame)
    pag1 = PageOne(nb)
    pag1.SetBackgroundColour(wx.Colour(166, 255, 166))
    nb.AddPage(pag1, "System Info")

    frame.Show()
    app.MainLoop()
