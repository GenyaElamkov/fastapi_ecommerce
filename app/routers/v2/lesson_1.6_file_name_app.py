'''
Самое простое поле для имени приложения
Создайте класс настроек для FastAPI-приложения с единственным полем my_app_name  
'(строка, по умолчанию значение "Simple App"). 
Настройки загружаются только из значений по умолчанию или переменных окружения (без .env файла).
Так же реализуйте FastAPI-эндпоинт /name, возвращающий имя приложения в формате {"my_app_name": cfg.my_app_name}.
Используйте синглтон и Depends.
'''

from fastapi import FastAPI
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    my_app_name: str = "Simple App"


cfg = Settings()

app = FastAPI()

@app.get("/name")
async def get_name():
    return {"my_app_name": cfg.my_app_name}