from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.routers.v1 import cart, categories, products, reviews, users

logger.add("info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message}]", level="INFO", enqueue = True)

app = FastAPI()


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    """Логирование"""
    log_id = str(uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to {request.url.path} failed")
            else:
                logger.info('Successfully accessed ' + request.url.path)
        except Exception as ex:
            logger.error(f"Request to {request.url.path} failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)
        return response
    

app_v1 = FastAPI(
    title="FastAPI Интернет-магазин",
    description="API для интернет-магазина v1",
    version="1.0.0"
)

app_v2 = FastAPI(
    title="FastAPI Интернет-магазин",
    description="API для интернет-магазина v2",
    version="2.0.0"
)

app.mount("/v1", app_v1)
app.mount("/v2", app_v2)
app.mount("/media", StaticFiles(directory="media"), name="media")

app_v1.include_router(categories.router)
app_v1.include_router(products.router)
app_v1.include_router(users.router)
app_v1.include_router(reviews.router)
app_v1.include_router(cart.router)


@app_v1.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API v1 работает.
    """
    content = {"message": "Добро пожаловать в API v2 интернет-магазина!"}
    return JSONResponse(content=content, media_type="application/json; charset=utf-8")

@app_v2.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API v2 работает.
    """
    content = {"message": "Добро пожаловать в API v1 интернет-магазина!"}
    return JSONResponse(content=content, media_type="application/json; charset=utf-8")
