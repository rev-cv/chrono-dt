from re import sub

class Formatter(object):
    """Класс посвящен методам преобразования даты в строку"""
    def __init__(self):
        super(Formatter, self).__init__()

        self.t_weekdays = {
            1: ['Понедельник', 'Пн', 'Пнд', 'Monday', 'Mo', 'Mon'],
            2: ['Вторник', 'Вт', 'Втр', 'Tuesday', 'Tu', 'Tue'],
            3: ['Среда', 'Ср', 'Сре', 'Wednesday', 'We', 'Wed'],
            4: ['Четверг', 'Чт', 'Чтв', 'Thursday', 'Th', 'Thu'],
            5: ['Пятница', 'Пт', 'Птн', 'Friday', 'Fr', 'Fri'],
            6: ['Суббота', 'Сб', 'Суб', 'Saturday', 'Sa', 'Sat'],
            0: ['Воскресенье', 'Вс', 'Вск', 'Sunday', 'Su', 'Sun'],
        }

        self.t_month_rus = ['', 
            'Январь', 'Февраль', 'Март', 
            'Апрель', 'Май', 'Июнь', 
            'Июль', 'Август', 'Сентябрь', 
            'Октябрь', 'Ноябрь', 'Декабрь'
        ]

        self.t_month_rus_abb = ['', 
            'Янв', 'Фев', 'Мар', 
            'Апр', 'Май', 'Июн', 
            'Июл', 'Авг', 'Сен', 
            'Окт', 'Ноя', 'Дек'
        ]

        self.t_month_eng = ['', 
            'January', 'February', 'March', 
            'April', 'May', 'June', 
            'July', 'August', 'September', 
            'October', 'November', 'December'
        ]

        self.t_month_eng_abb = ['', 
            'Jan', 'Feb', 'Mar', 
            'Apr', 'May', 'Jun', 
            'Jul', 'Aug', 'Sep', 
            'Oct', 'Nov', 'Dec'
        ]

    def F(self, temp = r"%a %b %d %H0:%M0:%S0 %Y %Z"):
        return self.format(temp)

    def T(self, temp = r"yyyy-MM-dd hh:mm:ss"):
        return self.template(temp)

    def template(self, temp = r"yyyy-MM-dd hh:mm:ss"):
        '''
        Метод предназначен только для шаблонов!

        yyyy - полный год
        yy   - год без века
        
        MM   - месяц с нулем
        MMMM - месяц текстом на английском (полный)
        MMM  - месяц текстом на английском (сокращенно)

        dd   - день с нулем
        ddd  - день недели текстом (сокращенно)
        dddd - день недели текстом (полный)

        hh - часы с нулем

        mm - минуты с нулем

        ss - секунды с нулем

        tz - временная зона
        ap - AM/PM
        '''

        regex = r'yyyy' # полный год
        if regex in temp:
            temp = sub(regex, f'{self.y}', temp)

        regex = r'yy'#год без века
        if regex in temp:
            temp = sub(regex, str(self.y)[-2:], temp)

        regex = r'MMMM'	#полное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng[self.m], temp)

        regex = r'MMM'	#сокращенное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng_abb[self.m], temp)

        regex = r'MM' # месяц с нулем
        if regex in temp:
            temp = sub(regex, f'{self.m:0>2}', temp)


        regex = r'dddd' # надпись дня недели на английском языке
        if regex in temp:
            temp = sub(regex, f'{self.t_weekdays[self.getWeekday()][3]}', temp)

        regex = r'ddd' # сокращеная надпись дня недели до трех символов на английском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][5], temp)

        regex = r'dd' # день с нулем
        if regex in temp:
            temp = sub(regex, f'{self.d:0>2}', temp)


        regex = r'hh'	#час с нулем
        if regex in temp:
            temp = sub(regex, f'{self.H:0>2}', temp)

        regex = r'mm'	#минуты с нулем
        if regex in temp:
            temp = sub(regex, f'{self.M:0>2}', temp)

        regex = r'ap'	#время в 12 часовом вормате
        if regex in temp:
            ap = "PM" if self.H > 12 else "AM"
            temp = sub( regex, ap, temp)

        regex = r'ss'	#секунды с нулем
        if regex in temp:
            temp = sub(regex, f'{self.S:0>2}', temp)

        return temp

    def format(self, temp = r"%a %b %d %H0:%M0:%S0 %Y %Z"):
        regex = r'%HMS0' 
        if regex in temp:
            text_str = self.format(r'%H0:%M0:%S0')
            temp = sub(regex, text_str, temp)

        regex = r'%HMS'
        if regex in temp:
            text_str = self.format(r'%H:%M:%S')
            temp = sub(regex, text_str, temp)

        regex = r'%YMD0'
        if regex in temp:
            text_str = self.format(r'%Y-%m0-%d0')
            temp = sub(regex, text_str, temp)

        regex = r'%YMD_'
        if regex in temp:
            text_str = self.format(r'%Y_%m0.%d0.')
            temp = sub(regex, text_str, temp)

        regex = r'%YMD'
        if regex in temp:
            text_str = self.format(r'%Y-%m-%d')
            temp = sub(regex, text_str, temp)

        regex = r'%x'
        if regex in temp:
            text_str = self.format(r'%Y-%m0-%d0')
            temp = sub(regex, text_str, temp)

        regex = r'%X'
        if regex in temp:
            text_str = self.format(r'%H0:%M0:%S0')
            temp = sub(regex, text_str, temp)

        regex = r'%DEC'	#декада месяца
        if regex in temp:
            dec = self.getDecade()
            temp = sub(regex, f'{dec}th', temp)

        regex = r'%DY'	#декада месяца, но отчет с начала года
        if regex in temp:
            dec = self.getDecadeYear()
            temp = sub(regex, f'{dec}th', temp)

        regex = r'%QUA'	#квартал года
        if regex in temp:
            qua = 'IV'
            if self.m < 4: qua = 'I'
            elif self.m < 7: qua = "II"
            elif self.m < 10: qua = "III"
            temp = sub(regex, f'{qua} quarter %Y', temp)

        regex = r'%Y'	#полный год
        if regex in temp:
            temp = sub(regex, f'{self.y}', temp)

        regex = r'%y'#год без века
        if regex in temp:
            temp = sub(regex, str(self.y)[-2:], temp)

        regex = r'%m0'	#номер месяца с нулем, если месяц январь-сентябрь
        if regex in temp:
            temp = sub(regex, f'{self.m:0>2}', temp)

        regex = r'%mE'	#полное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng[self.m], temp)

        regex = r'%mR'	#полное название месяца на русском языке языке
        if regex in temp:
            temp = sub(regex, self.t_month_rus[self.m], temp)

        regex = r'%mAE'	#сокращенное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng_abb[self.m], temp)

        regex = r'%mAR'	#сокращенное название месяца на русском языке
        if regex in temp:
            temp = sub(regex, self.t_month_rus_abb[self.m], temp)

        regex = r'%m'	#номер месяца без нуля, если месяц январь-сентябрь
        if regex in temp:
            temp = sub(regex, str(self.m), temp)

        regex = r'%B'	#полное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng[self.m], temp)

        regex = r'%b'	#сокращенное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng_abb[self.m], temp)

        regex = r'%d0'	#день месяца с нулем (05) в датах между 01-09
        if regex in temp:
            temp = sub(regex, f'{self.d:0>2}', temp)

        regex = r'%d'	#день месяца без нуля (5) в датах между 1-9
        if regex in temp:
            temp = sub(regex, str(self.d), temp)

        regex = r'%H0'	#час с нулем
        if regex in temp:
            temp = sub(regex, f'{self.H:0>2}', temp)

        regex = r'%H'	#час
        if regex in temp:
            temp = sub(regex, str(self.H), temp)

        regex = r'%M0'	#минуты с нулем
        if regex in temp:
            temp = sub(regex, f'{self.M:0>2}', temp)

        regex = r'%M'	#минуты
        if regex in temp:
            temp = sub(regex, str(self.M), temp)

        regex = r'%AMPM'	#время в 12 часовом вормате
        if regex in temp:
            temp = sub(
                regex, 
                f'{self.H-12}:{self.M}PM' if self.H > 12 else f'{self.H}:{self.M}AM', 
                temp
            )

        regex = r'%S0'	#секунды с нулем
        if regex in temp:
            temp = sub(regex, f'{self.S:0>2}', temp)

        regex = r'%S'	#секунды
        if regex in temp:
            temp = sub(regex, str(self.S), temp)

        regex = r'%Z'	#локальная зона
        if regex in temp:
            temp = sub(regex, f'{self.tz}', temp)

        regex = r'%wAE3'	#сокращеная надпись дня недели до трех символов на английском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][5], temp)

        regex = r'%wAR3'	#сокращеная надпись дня недели до трех символов на русском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][2], temp)

        regex = r'%wAR'	#сокращеная надпись дня недели до 2 символов на русском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][1], temp)

        regex = r'%wAE'	#сокращеная надпись дня недели до 2 символов на русском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][4], temp)

        regex = r'%wR'	#сокращеная надпись дня недели на русском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][0], temp)

        regex = r'%wE'	#сокращеная надпись дня недели на английском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][3], temp)

        regex = r'%w'	#день недели
        if regex in temp:
            temp = sub(regex, f'{self.getWeekday()}', temp)

        regex = r'%cRome'	#век римскими цифрами
        if regex in temp:
            temp = sub(regex, f'{self.getCenturyRome()}', temp)

        regex = r'%c'	#век арабскими цифрами
        if regex in temp:
            temp = sub(regex, f'{self.getCentury()}', temp)

        regex = r'%a'	#сокращеная надпись дня недели до трех символов на английском языке
        if regex in temp:
            temp = sub(regex, f'{self.t_weekdays[self.getWeekday()][5]}', temp)

        regex = r'%A'	#надпись дня недели на английском языке
        if regex in temp:
            temp = sub(regex, f'{self.t_weekdays[self.getWeekday()][3]}', temp)

        regex = r'%W'	#кол-во недель с начала года (считается с первого понедельника)
        if regex in temp:
            temp = sub(regex, str(self.getWeekYear()), temp)

        regex = r'%j'	#кол-во дней с начала года
        if regex in temp:
            temp = sub(regex, str(self.getDayYear()), temp)

        regex = r'%I'	#часы в 12часовом формате
        if regex in temp:
            temp = sub(
                regex, 
                f'{self.H-12}:{self.M}' if self.H > 12 else f'{self.H}:{self.M}', 
                temp
            )

        return temp


    def convertToRomanNumerals(self, arabic):
        # https://unicode-table.com/ru/sets/roman-numerals/
        result = ""

        def reduction (symbol_roman, arg):
            nonlocal arabic
            nonlocal result
            if arabic >= arg:
                while arabic >= arg:
                   result += symbol_roman 
                   arabic -= arg
        
        reduction('ↈ', 100000)
        reduction('ↇ', 50000)
        reduction('ↂ', 10000)
        reduction('ↁ', 5000)
        reduction('Ⅿ', 1000)
        reduction('Ⅾ', 500)
        reduction('Ⅽ', 100)
        reduction('Ⅼ', 50)
        reduction('Ⅹ', 10)

        if 0 < arabic < 10:
            r = {1:'Ⅰ',2:'Ⅱ',3:'Ⅲ',4:'Ⅳ',5:'Ⅴ',6:'Ⅵ',7:'Ⅶ',8:'Ⅷ',9:'Ⅸ',10:'Ⅹ'}
            result += r[arabic]

        return result 
        