from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_buyer, get_current_user
from app.db_depends import get_async_db
from app.grade import update_product_rating
from app.models.products import Product as ProductModel
from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.schemas import Review as ReviewSchema
from app.schemas import ReviewCreate as ReviewCreateSchema

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReviewSchema)
async def create_review(review: ReviewCreateSchema, 
                        db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_buyer),
                        ) -> ReviewSchema:
    """Добавляет отзыв"""
    result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == review.product_id, ProductModel.is_active == True)
    )
    product = result.first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found",
        )
        
    coincidence = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.user_id == current_user.id,
            ReviewModel.product_id == review.product_id,
        )
    )
    if coincidence.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="It is impossible to leave a review because a review already exists",
        )
    
    if review.grade > 5 or review.grade < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, 
            detail="Grade must be between 1 and 5",
        )
    db_review = ReviewModel(**review.model_dump(), user_id = current_user.id)
    db.add(db_review)
    await update_product_rating(db, product.id)
    await db.refresh(db_review)

    return db_review

    """Возвращает все отзывы"""
    result = await db.scalars(
        select(ReviewModel).where(ReviewModel.is_active == True)
    )
    reviews = result.all()
    return reviews


@router.delete("/{review_id}")
async def delete_review(review_id: int, 
                        db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_user),
                        ) -> dict:
    """Удаляет отзыв"""
    result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.id == review_id, ReviewModel.is_active == True,
        )
    )
    review = result.first()
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found",
        )
    
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only the author or an admin can delete this review"
        )
    review.is_active = False
    await update_product_rating(db, review.product_id)
    await db.refresh(review)
    return {"message": "Review deleted"}
