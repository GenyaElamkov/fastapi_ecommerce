'''
Настройка секретного ключа
Создайте класс настроек с полем secret_key (строка, по умолчанию значение "default-secret"). 

Настройки должны загружаться из .env файла.
Реализуйте эндпоинт /secret, возвращающий первые 4 символа ключа с добавлением "...".
Используйте синглтон и Depends.
'''

from functools import lru_cache

from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = "default-secret"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
    )

@lru_cache
def get_settings():
    return Settings()

app = FastAPI()

@app.get("/secret")
async def get_secret(cfg: Settings = Depends(get_settings)):
    return cfg.secret_key[:4] + "..."