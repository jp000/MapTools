# coding=utf-8
from __future__ import print_function, unicode_literals
import re

__version__ = 1.0


class stack:
    def __init__(self, size):
        self.size = size
        self._stk = []

    def push(self, value):
        self._stk.append(value)
        if len(self._stk) > self.size:
            self._stk.pop(0)

    def popAll(self):
        stk = self._stk[:]
        self._stk.clear()
        return stk

    @property
    def Count(self):
        return len(self._stk)


def process(parameters, filename, serachPattern):
    pat = re.compile(serachPattern)
    S = stack(parameters.contextBefore)
    post = 0
    matchCount = 0
    lineNumber = 0

    with open(filename, 'rb') as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            lineNumber += 1
            line = line.decode('utf8').strip('\n')
            m = pat.match(line)
            if not m:
                if post > 0:
                    if parameters.showNumber:
                        print('++{} {}'.format(lineNumber, line))
                    else:
                        print('++ {}'.format(line))
                    post -= 1
                else:
                    if 0 < parameters.maxMaches <= matchCount:
                        break
                    S.push(line)
            else:
                matchCount += 1
                tmpLineNumber = lineNumber - S.Count
                for linesBefore in S.popAll():
                    if parameters.showNumber:
                        print('--{} {}'.format(tmpLineNumber, linesBefore))
                        tmpLineNumber += 1
                    else:
                        print('-- {}'.format(linesBefore))
                if parameters.showNumber:
                    print('**{} {}'.format(lineNumber, line))
                else:
                    print('** {}'.format(line))

                post = parameters.contextAfter


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create batch file for the build process')
    parser.add_argument('--version', action='version', version='%(prog)s v{}'.format(__version__))
    parser.add_argument('filename', nargs='?', help='File to process')
    parser.add_argument('-B', '--contextBefore', action='store', type=int, default=0, help='Display n previous lines')
    parser.add_argument('-A', '--contextAfter', action='store', type=int, default=0, help='Display n post lines')
    parser.add_argument('-m', '--maxMaches', action='store', type=int, default=0, help='Stop after n matches')
    parser.add_argument('-p', '--serachPattern', action='store', required=True, help='Pattern to match')
    parser.add_argument('-N', '--showNumber', action='store_true', help='Show line numbers')

    opt = parser.parse_args()

    process(opt, opt.filename, opt.serachPattern)
