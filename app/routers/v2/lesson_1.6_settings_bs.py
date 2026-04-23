'''
Настройка базы данных
Создайте класс настроек с полями database_url (строка, по умолчанию "sqlite:///./app.db") и max_connections (целое число, по умолчанию 10). Настройки должны загружаться из .env файла.
Реализуйте FastAPI-эндпоинт /db, возвращающий эти настройки в формате {"database_url": cfg.database_url, "max_connections": cfg.max_connections}.
Используйте синглтон и Depends.
'''

from functools import lru_cache

from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    max_connections: int = 10
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()


app = FastAPI()

@app.get("/db")
async def db(cfg: Settings = Depends(get_settings)):
    return {"database_url": cfg.database_url, "max_connections": cfg.max_connections}