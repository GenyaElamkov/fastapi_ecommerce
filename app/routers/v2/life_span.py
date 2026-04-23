'''
Логирование старта и завершения приложения

Вам нужно создать FastAPI-приложение, которое будет логировать ключевые этапы своего жизненного цикла.

При запуске приложения должно выводиться сообщение в консоль: "Application is starting...".
При завершении работы приложения (например, при остановке сервера) должно выводиться сообщение: "Application is shutting down...".
Используйте @asynccontextmanager для управления жизненным циклом, чтобы обработать события запуска и завершения.
'''

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def life_span(app: FastAPI):
    logger.info("Application is starting...")
    yield
    logger.info("Application is shutting down...")

app = FastAPI(lifespan=life_span)