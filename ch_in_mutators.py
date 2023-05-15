import datetime
from ch_in_catchers import setFinish, setStart



def chgToStepInterval(s, step = 0, roundoff = "day", expansion = True):
    # получает следующий или предыдущий интервал в зависимости roundOff и количества шагов (step)

    if roundoff == "day":
        dts = datetime.datetime(*s) + datetime.timedelta(days=step)
        return [
            setStart((dts.year, dts.month, dts.day, 0, 0, 0), expansion, roundoff),
            setFinish((dts.year, dts.month, dts.day, 0, 0, 5), expansion, roundoff),
        ]
    
    elif roundoff == "week":
        dts = datetime.datetime(*s) + datetime.timedelta(days=step*7)
        return [
            setStart((dts.year, dts.month, dts.day, 0, 0, 0), expansion, roundoff),
            setFinish((dts.year, dts.month, dts.day, 0, 0, 5), expansion, roundoff),
        ]
    
    elif roundoff == "hour":
        dts = datetime.datetime(*s) + datetime.timedelta(hours=step)
        return [
            setStart((dts.year, dts.month, dts.day, 0, 0, 0), expansion, roundoff),
            setFinish((dts.year, dts.month, dts.day, 0, 0, 5), expansion, roundoff),
        ]

    elif roundoff == "minute":
        dts = datetime.datetime(*s) + datetime.timedelta(minutes=step)
        return [
            setStart((dts.year, dts.month, dts.day, 0, 0, 0), expansion, roundoff),
            setFinish((dts.year, dts.month, dts.day, 0, 0, 5), expansion, roundoff),
        ]

    elif roundoff == "year":
        return [
            setStart((s[0] + step, s[1], s[2], 0, 0, 0), expansion, roundoff),
            setFinish((s[0] + step, s[1], s[2], 0, 0, 5), expansion, roundoff),
        ]

    elif roundoff == "decennary":
        return [
            setStart((s[0] + step * 10, s[1], s[2], 0, 0, 0), expansion, roundoff),
            setFinish((s[0] + step * 10, s[1], s[2], 0, 0, 5), expansion, roundoff),
        ]

    elif roundoff == "month":
        y, m, *ttt = s
        if step < 0:
            while step < 0:
                if m - 1 == 0:
                    y, m = y - 1, 12
                else:
                    m = m - 1
                step += 1
        elif step > 0:
            while step > 0:
                if m + 1 > 12:
                    y, m = y + 1, 1
                else:
                    m += 1
                step -= 1
        return [
            setStart((y, m, 1, 0, 0, 0), expansion, roundoff),
            setFinish((y, m, 1, 0, 0, 5), expansion, roundoff),
        ]

    elif roundoff == "decade":
        y, m, d, *ttt = s
        if step < 0:
            while step < 0:
                if d < 11:
                    y = y if m-1 > 0 else y-1
                    m = m-1 if m-1 > 0 else 12
                    d = 21
                elif d < 21:
                    d = 1
                else:
                    d = 11
                step += 1
        elif step > 0:
            while step > 0:
                if d < 11:
                    d = 11
                elif d < 21:
                    d = 21
                else:
                    y = y if m < 12 else y+1
                    m = m + 1 if m < 12 else 1
                    d = 1
                step -= 1
        return [
            setStart((y, m, 1, 0, 0, 0), expansion, roundoff),
            setFinish((y, m, 1, 0, 0, 5), expansion, roundoff),
        ]
    
    elif roundoff == "quarter":
        y, m, *ttt = s
        if step < 0:
            while step < 0:
                if m <= 3:  
                    y, m = y - 1, 10  
                elif m <= 6:  
                    m = 1
                elif m <= 9:  
                    m = 4
                else:
                    m = 7
                step += 1
        elif step > 0:
            while step > 0:
                if m <= 3:  
                    m = 4
                elif m <= 6:
                    m = 7
                elif m <= 9:
                    m = 10
                else:
                    y, m = y + 1, 1
                step -= 1
        return [
            setStart((y, m, 1, 0, 0, 0), expansion, roundoff),
            setFinish((y, m, 1, 0, 0, 5), expansion, roundoff),
        ]

if __name__ == '__main__':
    print(chgToStepInterval((2023, 5, 12), 4, "decade"))
   