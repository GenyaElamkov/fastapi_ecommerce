'''
Игнорирование лишних переменных
Создайте класс настроек с полем log_level (строка, по умолчанию "INFO").
 Настройте его так, чтобы игнорировать лишние переменные окружения или записи в .env файле.
Реализуйте FastAPI-эндпоинт /log, возвращающий текущий уровень логирования.
Используйте синглтон и Depends.
'''

from functools import lru_cache

from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    log_level: str = "INFO"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        ignore_extra=True,
    )

@lru_cache
def get_settings():
    return Settings()

app = FastAPI()

@app.get("/log")
async def get_log_level(settings: Settings = Depends(get_settings)):
    return {"log_level": settings.log_level}