from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Для анализатора кода
if TYPE_CHECKING:
    from app.models.products import Product
    from app.models.users import User


class Category(Base):
    """Модель категории"""
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")
    admin: Mapped[list["User"]] = relationship("User", back_populates="categories")

    parent: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="children",
        remote_side="Category.id",
    )
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
