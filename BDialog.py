#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import wx

import BFrame
import BIcons
import BSettings

class BDialog(BFrame.MyFrame):
    def __init__(self, *args, **kwds):
        self.MainIcon = BIcons.catalog['JP-chapeau'].GetBitmap()
        self.ToolSave = BIcons.catalog['Save'].GetBitmap()
        self.ToolOpen = BIcons.catalog['OpenFolder'].GetBitmap()
        self.shift_down = False

        super().__init__(*args, **kwds)

        self.Bind(wx.EVT_CLOSE, self.OnClose, id=wx.ID_ANY)

        self.historyIds = [wx.NewId() for x in range(9)]
        self.Bind(wx.EVT_MENU, self.onFileId, None, self.historyIds[0], self.historyIds[-1])
        self.history = wx.FileHistory(maxFiles=9, idBase=self.historyIds[0])
        self.history.UseMenu(self.mnuFile)

    def OnClose(self, event):
        self.saveHistory()
        self.Destroy()

    def onFileId(self, event):
        fileName = self.history.GetHistoryFile(event.Id - self.historyIds[0])
        wx.GetApp().GetDataFromFile(fileName)
        self.StatusBar.SetStatusText('File: {}'.format(fileName))

    def onFileOpen(self, event):  # wxGlade: MyFrame.<event_handler>
        wildcard = "Text File (*.txt)|*.txt|" \
                   "All files (*.*)|*.*"
        app = wx.GetApp()
        fileName = app.m_fileName if hasattr(app, "m_fileName") else ""
        dirName = app.m_dirName if hasattr(app, "m_dirName") else ""
        dlg = wx.FileDialog(self, message="Open File",
                            defaultDir=dirName, defaultFile=fileName, wildcard=wildcard,
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.history.AddFileToHistory(dlg.GetPath())
            app.m_fileName = dlg.GetFilename()
            app.m_dirName = dlg.GetDirectory()
            wx.GetApp().GetDataFromFile(dlg.GetPath())
            self.StatusBar.SetStatusText('File: {}'.format(dlg.GetPath()))
        dlg.Destroy()

    def onFileSave(self, event):  # wxGlade: MyFrame.<event_handler>
        textCtrl = wx.Window.FindWindowById(self.ID_WIN)
        if textCtrl.Value == '':
            return
        wildcard = "Text File (*.txt)|*.txt|" \
                   "All files (*.*)|*.*"
        app = wx.GetApp()
        fileName = app.m_fileName if hasattr(app, "m_fileName") else ""
        dirName = app.m_dirName if hasattr(app, "m_dirName") else ""
        dlg = wx.FileDialog(self, message="Save to File",
                            defaultDir=dirName, defaultFile=fileName, wildcard=wildcard,
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            app.m_fileName = dlg.GetFilename()
            app.m_dirName = dlg.GetDirectory()
            textCtrl.SaveFile(dlg.GetPath())
        dlg.Destroy()

    def onFileExit(self, event):  # wxGlade: MyFrame.<event_handler>
        self.Close()

    def saveHistory(self):
        wx.GetApp().m_settings.history = []
        files = self.history.GetCount()
        for i in range(files):
            wx.GetApp().m_settings.history.append(self.history.GetHistoryFile(i))
        wx.GetApp().m_settings.Save()

    def loadHistory(self):
        files = wx.GetApp().m_settings.history
        if files is None:
            return
        for f in files:
            self.history.AddFileToHistory(f)

    def onUserAction(self, event):  # wxGlade: MyFrame.<event_handler>
            print("Event handler 'onUserAction' ID={}".format(event.GetId()))


class MyApp(wx.App):
    def OnInit(self):
        self.m_settings = BSettings.Settings('BApp', 'BApp.json')
        self.m_data = None
        self.frame = BDialog(None, wx.ID_ANY, "")
        self.frame.loadHistory()
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

    def GetDataFromFile(self, filename):
        with open(filename, 'rb') as fp:
            self.m_data = fp.read()


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
    v = app;