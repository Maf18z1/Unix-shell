# 1. Клонирование репозитория
Склонируйте репозиторий с исходным кодом и тестами:
'''git clone <URL репозитория>
cd <директория проекта>'''

# 2.Запуск окружения
#Активируйте виртуальное окружение
python -m venv venv
#Для Windows:
venv\Scripts\activate
#Для MacOS/Linux:
source venv/bin/activate
pip install pytest

python __main__.py

# 3.Структура проекта
Unixshell.py           # Файл с реализацией команд
Test.py      # Файл с тестами для команд
system.tar # архив с файловой системой

# 4.Запуск тестов
Мы будем использовать модуль Python pytest -v для тестирования.
pytest -v
