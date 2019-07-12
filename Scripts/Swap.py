try:
    hasNpp = notepad.getVersion() is not None
except:
    hasNpp = False

import re

def DoSwap2(sel, sep='\s*[,:;/]\s*'):
    x,y = re.split(sep, sel)
    return '{},{}'.format(y, x)

if __name__ == '__main__':
    if hasNpp:
        fileName = notepad.getCurrentFilename()
        console.show()
        console.clear()
        console.write('cmd={}\n'.format(notepad.getCommandLine()))
        num_selections = editor.getSelections()
        for sel_nbr in range(num_selections):
            start_pos = editor.getSelectionNStart(sel_nbr)
            end_pos = editor.getSelectionNEnd(sel_nbr)
            txt = editor.getTextRange(start_pos, end_pos)
            editor.replace(txt, DoSwap2(txt), 0, start_pos, end_pos)
    else:
        print("Not an npp environment")