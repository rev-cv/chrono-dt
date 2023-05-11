import datetime
import pytz

# Создаем объект datetime с локальной временной зоной
local_time = datetime.datetime.now()

# Создаем объекты tzinfo с разными часовыми поясами
local_tz = pytz.timezone('Europe/Moscow') # Москва
new_tz = pytz.timezone('America/New_York') # Нью-Йорк

# Локализуем объект datetime с локальной временной зоной
local_time = local_tz.localize(local_time)

# Переводим объект datetime в новую временную зону
new_time = local_time.astimezone(new_tz)

# Выводим результаты
print(local_time) # 2021-12-25 12:00:00+03:00
print(new_time) # 2021-12-25 04:00:00-05:00 
