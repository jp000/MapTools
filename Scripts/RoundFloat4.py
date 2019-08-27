try:
    eol = ('\r\n', '\r', '\n')[editor.getEOLMode()]
    getSelText = editor.getSelText
    selectAll = editor.selectAll
    replaceSel = editor.replaceSel
    appendText = editor.appendText

except:
    from win32clipboard import (
        OpenClipboard, SetClipboardText, CloseClipboard, EnumClipboardFormats,
        GetClipboardData, EmptyClipboard, IsClipboardFormatAvailable,
        RegisterClipboardFormat, SetClipboardData,
        CF_TEXT, CF_UNICODETEXT, CF_OEMTEXT, CF_HDROP)

    eol = '\n'
    def getSelText():
        txt = None
        OpenClipboard()
        try:
            if IsClipboardFormatAvailable(CF_UNICODETEXT):
                txt = GetClipboardData(CF_UNICODETEXT)
            elif IsClipboardFormatAvailable(CF_TEXT):
                txt = GetClipboardData(CF_TEXT).decode('utf-8')
        finally:
            CloseClipboard()
        return txt
    def selectAll():
        pass
    def replaceSel(data):
        print(data)
    def appendText(txt):
        print(txt)

import re

pattern = re.compile(r'[-+]?\d*\.\d+|\d+')

def Replace(data, digits):
    return pattern.sub(
        lambda m: '{{:.{}f}}'.format(digits).format(float(m.group(0))), data)

if __name__ == '__main__':
    txt = getSelText()
        if txt == '':
        selectAll()
        txt = getSelText()
    if txt is not None:
        replaceSel(Replace(txt, 4))
        appendText(eol)


