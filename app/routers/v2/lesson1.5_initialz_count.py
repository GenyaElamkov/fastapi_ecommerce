'''
Инициализация счетчика запросов

Разработайте FastAPI-приложение, которое подсчитывает количество HTTP-запросов, 
сделанных к эндпоинту, в течение своего жизненного цикла.

При запуске приложение должно инициализировать счётчик app.state.request_count значением 0 
и вывести в консоль сообщение: "Request counter initialized".
При завершении работы приложение должно вывести в консоль общее количество запросов в формате: "Total requests: X", 
где X — значение счетчика.
Добавьте эндпоинт GET /, который возвращает JSON в формате {"message": "Hello, World!"} и увеличивает счетчик на 1 при каждом вызове.

Используйте @asynccontextmanager для управления жизненным циклом.
'''

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def life_span(app: FastAPI):
    app.state.request_count = 0
    logger.info("Request counter initialized")
    
    yield
    logging.info(f"Total requests: {app.state.request_count}")

app = FastAPI(lifespan=life_span)

@app.get("/")
async def root():
    app.state.request_count += 1
    return {"message": "Hello, World!"}