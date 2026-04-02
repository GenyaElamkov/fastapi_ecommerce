from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_seller
from app.db_depends import get_async_db
from app.models import Category as CategoryModel
from app.models import Product as ProductModel
from app.models import Review as ReviewModel
from app.models import User as UserModel
from app.schemas import Product as ProductSchema
from app.schemas import ProductCreate as ProductCreateSchema
from app.schemas import Review as ReviewSchema

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: AsyncSession = Depends(get_async_db)) -> list[ProductSchema]:
    """Возвращает все товары"""
    result = await db.scalars(
        select(ProductModel).join(CategoryModel).where(
            ProductModel.is_active == True,   # noqa
            CategoryModel.is_active == True,   # noqa
            ProductModel.stock > 0,
        ),
    )
    products = result.all()
    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
) -> ProductSchema:
    """Добавление нового товара"""
    result = await db.scalars(
        select(CategoryModel).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active == True,    # noqa
        ),
    )
    category = result.first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found or inactive",
        )
    db_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
) -> list[ProductSchema]:
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    result_category = await db.scalars(
        select(CategoryModel).where(
            CategoryModel.id == category_id,
            CategoryModel.is_active == True,    # noqa
        ),
    )
    category = result_category.first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or inactive",
        )
    result_products = await db.scalars(
        select(ProductModel).where(
            ProductModel.category_id == category_id,
            ProductModel.is_active == True, # noqa
        ),
    )
    products = result_products.all()

    return products


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, 
                      db: AsyncSession = Depends(get_async_db),
                      ) -> ProductSchema:
    """Возвращает товар по его ID"""
    stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True, # noqa
    )
    result_product = await db.scalars(stmt)
    product = result_product.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive",
        )
    category_result = await db.scalars(
        select(CategoryModel).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active == True,    # noqa
        ),
    )
    category = category_result.first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found or inactive",
        )
    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductCreateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
) -> ProductSchema:
    """Обновление товоров"""
    product_result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == product_id,
            ProductModel.is_active == True, # noqa
        ),
    )
    db_product = product_result.first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive",
        )
    if db_product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own products",
        )
    category_result = await db.scalars(
        select(CategoryModel).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active == True,    # noqa
        ),
    )
    db_category = category_result.first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found or inactive",
        )

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump()),
    )
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
) -> dict:
    """Удаление товара"""
    product_result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == product_id,
            ProductModel.is_active == True, # noqa
        ),
    )
    product = product_result.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive",
        )
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own products",
        )
    product.is_active = False
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/{product_id}/reviews/", response_model=list[ReviewSchema])
async def get_product_reviews(product_id: int, 
                              db: AsyncSession = Depends(get_async_db),
                              ) -> list[ReviewSchema]:
    """Возвращает список отзывов в указанном продукте по её ID."""
    product_result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == product_id,
            ProductModel.is_active == True,
        )
    )
    if product_result.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found or inactive",
        )
    reviews = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.product_id == product_id, 
            ReviewModel.is_active == True,
        )
    )
    return reviews.all()