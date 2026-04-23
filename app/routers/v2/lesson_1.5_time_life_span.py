'''
Подсчет времени работы приложения

Создайте FastAPI-приложение, которое отслеживает время своей работы.

При запуске приложение должно зафиксировать текущее время в глобальной переменной.
При завершении работы приложение должно вычислить, сколько секунд оно работало,
 и вывести это значение в консоль в формате: "Application ran for X.XX seconds", 
 где X.XX — время в секундах с двумя знаками после запятой.
Используйте @asynccontextmanager для управления жизненным циклом, 
а для работы с временем — модуль time. Убедитесь, что время корректно фиксируется и выводится.
'''

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def life_span(app: FastAPI):
    start = time.time()
    yield
    finish = time.time()
    result_time = finish - start
    logger.info(f"Application ran for {result_time:.2f} seconds")

app = FastAPI(lifespan=life_span)