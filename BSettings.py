# -*- coding: utf-8 -*-

__author__ = 'JPE'
__created__ = '09.04.13 09:03'

from os import makedirs
from os.path import dirname, join, exists
import json
from types import SimpleNamespace as Namespace

def GetSpecialFile(CSIDL):
    import ctypes
    from ctypes import wintypes

    LPSTR = wintypes.LPSTR

    SHGetFolderPath = ctypes.windll.shell32.SHGetFolderPathA
    SHGetFolderPath.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.HANDLE, wintypes.DWORD, LPSTR]
    SHGetFolderPath.restype = wintypes.LONG

    pszPath = ctypes.create_string_buffer(wintypes.MAX_PATH)

    try:
        hResult = SHGetFolderPath(0, CSIDL, 0, 0, pszPath)
    except:
        hResult = 1
    if hResult == 0:
        return pszPath.value
    else:
        return None

def getLocalDir():
    LOCALAPPDATA = 0x1C
    return GetSpecialFile(LOCALAPPDATA).decode('utf-8')

class Settings(object):
    def __init__(self, app='BApp', filename='BApp.json'):
        localDir = getLocalDir()
        SettingsFileName = join(localDir, app, filename)
        try:
            with open(SettingsFileName, "rb") as fp:
                data = json.load(fp)
                self.__dict__ = data
        except:
            pass
        self.SettingsFileName = SettingsFileName

    def Save(self):
        path = dirname(self.SettingsFileName)
        if not exists(path):
            makedirs(path)
        with open(self.SettingsFileName, "wb") as fp:
            del self.SettingsFileName
            fp.write(json.dumps(self.__dict__).encode('utf-8'))

    def __getattr__(self, item):
        return None
