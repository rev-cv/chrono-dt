
def arabToRoman(arabic):
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
