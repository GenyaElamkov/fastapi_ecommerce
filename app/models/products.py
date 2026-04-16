from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (Boolean, Computed, DateTime, Float, ForeignKey, Index,
                        Integer, Numeric, String, func, text)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Для анализатора кода
if TYPE_CHECKING:
    from app.models.cart_items import CartItem
    from app.models.categories import Category
    from app.models.reviews import Review
    from app.models.users import User


class Product(Base):
    """Модель продукта"""
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, server_default=text('0'))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), 
                                                 server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    tsv: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed(
            """
            setweight(to_tsvector('english', coalesce(name, '')), 'A')
            || 
            setweight(to_tsvector('english', coalesce(description, '')), 'B')
            """,
            persisted=True,
        ),
        nullable=False
    )

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    seller: Mapped["User"] = relationship("User", back_populates="products")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="product")
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")

    __table__args__ = (
        Index("ix_products_tsv_gin", "tsv", postgresql_using="gin"),
    )
    