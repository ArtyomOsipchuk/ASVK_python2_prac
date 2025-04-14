import locale

print(locale.getlocale())

# bash
# LC_ALL=en_US.UTF-8

setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

# pipenv install -d
# значит -dev типа только для разработки зависимость
