from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.cart_items import CartItem
    from app.models.categories import Category
    from app.models.products import Product
    from app.models.reviews import Review


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String, default="buer")   # buer or seller

    products: Mapped[list["Product"]] = relationship("Product", back_populates="seller")
    categories: Mapped[list["Category"]] = relationship("Category", back_populates="admin")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user")

    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
