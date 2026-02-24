from fastapi import APIRouter

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/")
async def get_all_products() -> dict:
    return {"message": "Список всех продуктов (заглушка)"}


@router.post("/")
async def create_product():
    return {"message": "Продукт создан (заглушка)"}


@router.get("/category/{category_id}")
async def get_products_by_category(category_id: int):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    return {"message": f"Товары в категории {category_id} (заглушка)"}


@router.get("/{product_id}")
async def get_product(product_id: int) -> dict:
    return {"message": f"Детали товара {product_id} (заглушка)"}


@router.put("/{product_id}")
async def create_products(products_id: int):
    return {"message": f"Продукт с ID {products_id} обновлена (заглушка)"}


@router.delete("/{product_id}")
async def delete_product(product_id):
    return {"message": f"Продукт с ID {product_id} удален (заглушка)"}
