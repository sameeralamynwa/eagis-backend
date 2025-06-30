from datetime import datetime
from typing import TYPE_CHECKING, List
from core.base_model import BaseModel
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Table, Text # <<< FIX: Import Text type
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql
from .enums import UserType, Permissions, OtpPurpose

if TYPE_CHECKING:
    from apps.images.models import Image

# ... (user_role_link and User class are unchanged) ...

user_role_link = Table(
    "user_role_link",
    BaseModel.metadata,
    Column("user.id", ForeignKey("user.id", ondelete="CASCADE")),
    Column("role_id", ForeignKey("role.id", ondelete="CASCADE")),
)


class User(BaseModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(), unique=True)
    password: Mapped[str] = mapped_column(String())
    is_active: Mapped[bool] = mapped_column(Boolean(), default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean(), default=False)
    user_type: Mapped[UserType] = mapped_column(
        postgresql.ENUM(UserType), default=UserType.User
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    roles: Mapped[list["Role"]] = relationship(
        back_populates="users", secondary=user_role_link
    )
    profile: Mapped["Profile"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        single_parent=True,
        passive_deletes=True,
    )
    images: Mapped[List["Image"]] = relationship(
        "Image",
        back_populates="uploaded_by",
        cascade="all, delete-orphan",
        single_parent=True,
        passive_deletes=True,
    )


class Role(BaseModel):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    permissions: Mapped[List[Permissions]] = mapped_column(
        postgresql.ARRAY(String()), default=[]
    )
    users: Mapped[List[User]] = relationship(
        back_populates="roles", secondary=user_role_link
    )


class Profile(BaseModel):
    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    avatar: Mapped[str | None] = mapped_column(String(), default=None)
    about: Mapped[str | None] = mapped_column(Text(), default=None)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship(
        back_populates="profile",
    )


class Otp(BaseModel):
    __tablename__ = "otp"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String())
    otp_hash: Mapped[str] = mapped_column(String())
    purpose: Mapped[OtpPurpose] = mapped_column(postgresql.ENUM(OtpPurpose))
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_used: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )