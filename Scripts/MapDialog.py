#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import wx

import MyFrame
import MyEmoji, Tools

class MapDialog(MyFrame.MyFrame):
    def __init__(self, *args, **kwds):
        self.mainIcon = MyEmoji.img.GetBitmap()
        self.toolsOpen = Tools.catalog['Open'].GetBitmap()
        self.toolsSave = Tools.catalog['Save'].GetBitmap()
        super(MapDialog, self).__init__(*args, **kwds)
#        _icon = MyEmoji.img.GetIcon()
#        self.SetIcon(_icon)


    def onToolOpen(self, event):
        with wx.FileDialog(None, "Select a file", wildcard='GEOJSON|*.geojson|All (*.*)|*.*',
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            dlg.FilterIndex = 0
            if dlg.ShowModal() == wx.ID_OK:
                fileName = dlg.GetPath()
                self.txtTop.AppendText(fileName + '\n')
                try:
                    if hasattr(self, 'processFile') and callable(self.processFile):
                        self.processFile(fileName, self.txtTop.AppendText)
                except:
                    self.txtBottom.AppendText('"processFile" not found or not callable\n')

    def onToolSave(self, event):
        print("Event handler 'onToolSave' not implemented!")
        event.Skip()

    def OnClose(self, event):
        self.Close()
