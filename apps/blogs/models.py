from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from core.base_model import BaseModel
from sqlalchemy.dialects import postgresql
from sqlalchemy import DateTime, String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from apps.images.models import Image


class Blog(BaseModel):
    __tablename__ = "blog"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(String)
    is_published: Mapped[bool] = mapped_column(default=False)
    short_desc: Mapped[str | None] = mapped_column(String, default=None)
    content: Mapped[str | None] = mapped_column(postgresql.TEXT, default=None)
    meta_title: Mapped[str | None] = mapped_column(String(100), default=None)
    meta_keywords: Mapped[str | None] = mapped_column(String(100), default=None)
    meta_desc: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("blog_category.id", ondelete="SET NULL"), default=None
    )
    category: Mapped[Optional["BlogCategory"]] = relationship(back_populates="blogs")
    thumbnail_id: Mapped[int | None] = mapped_column(
        ForeignKey("image.id", ondelete="SET NULL"), default=None
    )
    thumbnail: Mapped[Optional["Image"]] = relationship()


class BlogCategory(BaseModel):
    __tablename__ = "blog_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(50))
    is_published: Mapped[bool] = mapped_column(default=False)
    short_desc: Mapped[str | None] = mapped_column(String, default=None)
    meta_title: Mapped[str | None] = mapped_column(String(100), default=None)
    meta_keywords: Mapped[str | None] = mapped_column(String(100), default=None)
    meta_desc: Mapped[str | None] = mapped_column(String, default=None)
    blogs: Mapped[List[Blog]] = relationship(back_populates="category")
    thumbnail_id: Mapped[int | None] = mapped_column(
        ForeignKey("image.id", ondelete="SET NULL")
    )
    thumbnail: Mapped[Optional["Image"]] = relationship()
