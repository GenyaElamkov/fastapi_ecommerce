from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_seller
from app.db_depends import get_async_db
from app.models import Category as CategoryModel
from app.models import Product as ProductModel
from app.models import Review as ReviewModel
from app.models import User as UserModel
from app.schemas import Product as ProductSchema
from app.schemas import ProductCreate as ProductCreateSchema
from app.schemas import ProductList as ProductListSchema
from app.schemas import ProductsRequest as ProductFilterSchema
from app.schemas import Review as ReviewSchema

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=ProductListSchema)
async def get_all_products(request: ProductFilterSchema  = Depends(),
                            db: AsyncSession = Depends(get_async_db),
    ) -> ProductListSchema:
    """Возвращает все товары"""
    if request.min_price is not None and request.max_price is not None and request.min_price > request.max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price не может быть больше max_price",
        )

    filters = [ProductModel.is_active == True]    # noqa
    if request.category_id is not None:
        filters.append(ProductModel.category_id == request.category_id)
    if request.min_price is not None:
        filters.append(ProductModel.price >= request.min_price)
    if request.max_price is not None:
        filters.append(ProductModel.price <= request.max_price)
    if request.in_stock is not None:
        filters.append(ProductModel.stock > 0 if request.in_stock else ProductModel.stock == 0)
    if request.seller_id is not None:
        filters.append(ProductModel.seller_id == request.seller_id)
    
    data_sort =[]
    if request.created is not None:
        data_sort.append(ProductModel.created_at.desc() if request.created else ProductModel.created_at.asc())
    else:
        data_sort.append(ProductModel.id)

    if request.search is not None:
        search_value = request.search.strip()
        if search_value:
            filters.append(func.lower(ProductModel.name).like(f"%{search_value.lower()}%"))
                           
    total_stmt = select(func.count()).select_from(ProductModel).where(*filters)
    total = await db.scalar(total_stmt) or 0

    product_stm = (
        select(ProductModel)
        .where(*filters)
        .order_by(*data_sort)
        .offset((request.page - 1) * request.page_size)
        .limit(request.page_size)
    )
    items = (await db.scalars(product_stm)).all()
    return {
        "items": items,
        "total": total,
        "page": request.page,
        "page_size": request.page_size,
    }


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


@router.get("/{product_id}/reviews/", response_model=list[ReviewSchema])
async def get_product_reviews(product_id: int, 
                              db: AsyncSession = Depends(get_async_db),
                              ) -> list[ReviewSchema]:
    """Возвращает список отзывов в указанном продукте по ID."""
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
