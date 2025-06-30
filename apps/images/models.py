from typing import TYPE_CHECKING
from core.base_model import BaseModel
from datetime import datetime
from sqlalchemy import DateTime, String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from apps.auth.models import User


class Image(BaseModel):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String())
    alt_text: Mapped[str | None] = mapped_column(String(), default=None)
    title: Mapped[str | None] = mapped_column(String(), default=None)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    uploaded_by: Mapped["User"] = relationship(
        "User",
        back_populates="images",
    )
