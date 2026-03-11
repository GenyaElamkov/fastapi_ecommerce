from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db_depends import get_db
from app.models import Category as CategoryModel
from app.models import Product as ProductModel
from app.schemas import Product as ProductSchema
from app.schemas import ProductCreate as ProductCreateSchema

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_db)) -> dict:
    stmt = select(ProductModel).where(ProductModel.is_active == True)   # noqa
    products = db.scalars(stmt).all()
    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreateSchema, db: Session = Depends(get_db)):
    if product.category_id is not None:
        stmt = select(CategoryModel).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active == True,    # noqa
        )
        category = db.scalars(stmt).first()
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found or inactive",
            )
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active == True,    # noqa
    )
    category = db.scalars(stmt).first()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or inactive",
        )
    product_stmt = select(ProductModel).where(
        ProductModel.category_id == category_id,
        ProductModel.is_active == True, # noqa
    )
    products = db.scalars(product_stmt).all()
    return products


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True, # noqa
    )
    product = db.scalars(stmt).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive",
        )
    return product


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreateSchema, db: Session = Depends(get_db)):
    stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True, # noqa
    )
    db_product = db.scalars(stmt).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive",
        )

    stmt = select(CategoryModel).where(
        CategoryModel.id == product.category_id,
        CategoryModel.is_active == True,    # noqa
    )
    db_category = db.scalars(stmt).first()
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found or inactive",
        )

    db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump()),
    )
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id, db: Session = Depends(get_db)):
    stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True, # noqa
    )
    product = db.scalars(stmt).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive",
        )
    product.is_active = False
    db.commit()
    return {"status": "success", "message": "Product marked as inactive"}
