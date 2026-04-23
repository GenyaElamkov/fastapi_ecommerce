'''
Создание временного файла при старте

Разработайте FastAPI-приложение, которое управляет временным файлом в течение своего жизненного цикла.

При запуске приложение должно создать текстовый файл temp.txt 
в текущей директории и записать в него строку "Hello, FastAPI!". 
Также в консоль должно быть выведено сообщение: "Temporary file created".
При завершении работы приложение должно проверить, существует ли файл temp.txt, и, если он существует, удалить его, 
выведя в консоль сообщение: "Temporary file deleted".
Используйте @asynccontextmanager для реализации и модуль os для работы с файлами. Убедитесь, что файл корректно создается и удаляется.
'''


import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEMP_FILE = "temp.txt"

@asynccontextmanager
async def life_span(app: FastAPI):
    with open(TEMP_FILE, "w") as f:
        f.write("Hello, FastAPI!")
        logging.info("Temporary file created")
    yield
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
        logging.info("Temporary file deleted")


app = FastAPI(lifespan=life_span) 