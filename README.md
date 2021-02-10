# chrono-dt
 python-модуль для упрощения работы со временем для ненагруженных проектов

```python
from chronodt import chrono
```

## Создание объекта chrono

```python
#создать объект с текущим локальным временем
c = chrono()

#создать объект передав год, месяц, день, час, минуты, секунды
#не переданным значениям будут проставлены минимальные возможные значение
c = chrono(2021, 2, 15, 12)

#создать объект передав строку в формате 
#1. 2021021512 - последовательность цифр
#2. 2021/02/15/12 в которой знак "/" может быть заменен любым символом или буквой
#3. формат ISO - "2020-05-14T08:20:30"
c = chrono("2021-02-15 12:00")

#создать объект передав в него chrono другой объект
c = chrono(chrono("2021-02-15 12:00"))

#создать объект передав в него datetime
c = chrono(datetime)

#создать объект передав в него QDateTime
c = chrono(QDateTime)

#создать объект передав в него QDate и опционально QTime
c = chrono(QDate, QTime)

#создать объект передав в него время в формате UnixEpoh
```
## Управление временными зонами
По умолчанию временная зона создаваемого объекта соответствует временной зоне на компьютере. Исключением является передача в создаваемый объект UnixEpoh или ISO - они всегда соответствуют временной зоне UTC.

При создании объекта можно указать конкретную временную зону передаваемой даты, а после произвести операции по переводу времени к нужной временной зоне.
```python
c = chrono(2021, 2, 15, TimeZone = "UTC")

#узнать временную зону объекта
print(c.timezone)

#перевести время в local-zone
c.toLocal()

#перевести время в UTC
c.toUTC()

#перевести время к указанной зоне
c.toTimeZone('UTC')

#просмотреть обозначения зон
print(c.getAllTimeZones())

#так же можно проверить содержит ли объект локальную дату или UTC
c.isUTC()
c.isLocal()
```
## Получение данных
```python

#год, месяц, день, час, минуты, секунды, временная зона
year, momth, day, h, m, s, timezone = c.year, c.month, c.day, c.hour, c.minute, c.second, c.timezone

#строка в формате ISO (всегда UTC)
str_iso = c.getISO()

#число UnixEpoch (всегда UTC)
ue = c.getUnixEpoch()

#объект datetime
dt = c.getDateTime()

#QDate из модуля PyQt5
qd = c.getQDate()

#QDateTime из модуля PyQt5
qdt = c.getQDateTime()

#QTime из модуля PyQt5
qt = c.getQTime()

#день недели
wd = c.getWeekday()

#день с начала года
dy = c.getDayYear()

#век
century = c.getCentury()

#век римскими цифрами
centuryRome = c.getCenturyRome()

#неделя года начиная с первого понедельника
w = c.getWeekYear()
```
## Смещение времени
Базовая функция смещения времени
```python
c.shift(year = -56, month = 0, day = 30, hour = 0, minute = 49, second = 15, week = 2)
```
Так же время можно смещать при помощи текстовых команд переданных в виде строки
```python
c.shiftTC("-56y 30d 49 15s 2w")
```
## Форматирование строки по шаблону
```python
c.format("Start %Y, %d %wAE3")
#>>> "Start 2021, 15 Feb"
```
Шаблон | Описание 
--- | ---
%Y  | полный год *2021*
%y  | сокращенный год *21*
%m  | месяц числом
%m0 | месяц числом. Если месяц меньше октября, то записывается с нулем *февраль - 02*
%d  | день числом
%d0 | день числом. Если день меньше 10, то записывается с нулем *09*
%H  | час
%H0 | час. Если час меньше 10, то записывается с нулем *05*
%I  | часы в 12 часовом формате
%M  | минуты
%M0 | минуты. Если минуты меньше 10, то записывается с нулем *05*
%S  | секунды
%S0 | секунды. Если секунд меньше 10, то записывается с нулем *05*
%W  |	кол-во недель с начала года (считается с первого понедельника)
%j  |	кол-во дней с начала года
%w  | день недели числом
%Z  | локальная зона
%DEC   | декада месяца *I decade of January*
%QUA   | квартал года  *I quarter 2021*
%c     | век арабскими цифрами *20*
%cRome | век римскими цифрами *XXI*
%B    | полное название месяца на английском языке *February*
%mE   | полное название месяца на английском языке *February*
%mR   | полное название месяца на русском языке *Февраль*
%b    | сокращенное название месяца на английском языке *Feb*
%mAE  | сокращенное название месяца на английском языке *Feb*
%mAR  | сокращенное название месяца на русском языке *Фев*
%wE   | полное название дня недели на английском языке *Monday*
%wR   | полное название дня недели на русском языке *Понедельник*
%wAE  | сокращенное до 2х символов название дня недели на английском языке *Mo*
%wAR  | сокращенное до 2х символов название дня недели на русском языке *Mo*
%wAE3 | сокращенное до 3х символов название дня недели на английском языке *Mon*
%wAR3 | сокращенное до 3х символов название дня недели на русском языке *Пнд*
%x    | запись даты. Аналогично шаблону %Y-%m0-%d0 *2021-02-15*
%X    | запись времени. Аналогично шаблону %H0:%M0:%S0 *15:00:00*
%YMD  | запись даты. Аналогично шаблону %Y-%m-%d *2021-2-15*
%YMD0 | запись даты. Аналогично шаблону %Y-%m0-%d0 *2021-02-15*
%YMD_ | запись даты. Аналогично шаблону %Y_%m0-%d0 *2021_02-15*
%AMPM | запись времени в 12часовом формате *3:00PM*
%HMS  | запись времени. Аналогично шаблону %H:%M:%S *15:0:0*
%HMS0 | запись времени. Аналогично шаблону %H0:%M0:%S0 *15:00:00*

## Внесение изменений в объект chrono
```python
c.setNow()
c.setUnixEpoch(UnixEpoch)
c.setDate(2021, 2, 15)
c.setTime(12, 40, 25)
c.setDateTimeChrono(obj_chrono)
c.setDateTime(datetime)
c.setDateTimeISO("2021-02-15T08:20:30")
c.setDateTimeStandartChrono("Tue Jun 23 18:42:36 2020 Asia/Yekaterinburg")
c.setDateTimeStr("2021-02-15 12:00:15")
c.setQDate(q_date)
c.setQDateTime(q_date_time)
c.setQTime(q_time)
```
## Операции с датами
*!плохо отлажено на текущий момент*

<, >, ==, <=, >=, !=

Вычитая один объект chrono из другого возвращается объект pchrono, содержащий период двух дат.
