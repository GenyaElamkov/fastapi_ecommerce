'''
Валидация режима окружения
Создайте класс настроек с полем environment, которое принимает только 
значения "dev", "test" или "prod" (по умолчанию "dev").
Настройки должны загружаться из .env файла.
Реализуйте FastAPI-эндпоинт /env, возвращающий текущий режим окружения.
Используйте синглтон и Depends.
'''

from functools import lru_cache

from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "dev"
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()


app = FastAPI()

@app.get("/env")
async def get_env(settings: Settings = Depends(Settings)):
    return {"environment": settings.environment}
