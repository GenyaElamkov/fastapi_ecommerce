'''
Префикс для переменных окружения
Создайте класс настроек с полями app_name (строка, по умолчанию "FastAPI App") и api_version (строка, по умолчанию "v1"). 
Настройки должны загружаться из .env файла с префиксом "APP_".
Реализуйте FastAPI-эндпоинт /info, возвращающий эти настройки в формате {"app_name": cfg.app_name, "api_version": cfg.api_version}.
Используйте синглтон и Depends.
'''
from functools import lru_cache

from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    api_version: str = "v1"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_"
    )

@lru_cache
def get_settings(): 
    return Settings()

app = FastAPI()

@app.get("/info")
async def info(cfg: Settings = Depends(get_settings)):
    return {"app_name": cfg.app_name, "api_version": cfg.api_version}