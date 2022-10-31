from Chrono.ch_transformator import chrono_transformator
from Chrono.ch_catcher import chrono_catcher
from Chrono.ch_pitcher import chrono_pitcher
from Chrono.ch_analyzer import chrono_analyzer
from String.string_deconstruction import Deconstruction
from String.string_construction import Formatter

class chrono( chrono_catcher, chrono_analyzer, chrono_pitcher,
        chrono_transformator, Deconstruction, Formatter ):

    def __init__(self, 
            y = None, m = None, d = None, 
            H = None, M = None, S = None, 
            shift = None, tz = "local"):

        super(chrono, self).__init__()

        self.chrono = chrono
        self.y = None
        self.m = None
        self.d = None
        self.H = None
        self.M = None
        self.S = None
        self.tz = None

        self.setTimeZone(tz)
        # в начале задается временная зода, 
        # чтобы не перезаписать временную зону
        # которая может прийти в аргументах
        self.set(y, m, d, H, M, S)

        if shift is not None:
            if type(shift) is str:
                # принимает строку с текстовыми командами для смещения
                self.shiftTextCommand(shift)
            elif type(shift) is dict:
                # принимает словарь с текстовыми командами для смещения
                self.shift(**shift)

    def __str__(self):
        s = 'Object.Chrono('
        s += 'DATE %Y-%m0-%d0; ' if self.isDate() else 'DATE None '
        s += 'TIME %H0:%M0:%S0; ' if self.isTime() else 'TIME None '
        s += 'TZ %Z;)'
        return self.format(s)

if __name__ == '__main__':
    # a = chrono("NOW")
    # print(a)
    # b = chrono(a)
    # print(b)
    
    # from PyQt5.QtCore import QDateTime

    # time = QDateTime(2022, 11, 20, 11, 34, 34)
    # tz = time.timeZone()

    # for x in QTimeZone().availableTimeZoneIds():
    # 	x = x.__str__()
    # 	print(type(x), x[2:-1], len(x))

    a = chrono("20221215", shift="-2y")
    print(a)

