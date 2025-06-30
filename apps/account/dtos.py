# apps/account/dtos.py

from datetime import datetime
from typing import Annotated, Optional
from fastapi import File, UploadFile
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from apps.auth.enums import Permissions, UserType


class RelatedRole(BaseModel):
    id: int
    name: str
    permissions: list[Permissions] = []


class RelatedProfile(BaseModel):
    id: int
    avatar: str | None = None
    # <<< FIX: Add 'about' field to the response DTO
    about: str | None = None


class AccountDetailRead(BaseModel):
    id: int
    name: str
    username: str
    email: str
    is_active: bool
    email_verified: bool
    user_type: UserType
    created_at: datetime
    updated_at: datetime
    roles: list[RelatedRole] = []
    profile: RelatedProfile


class UpdateAccountDetailForm(BaseModel):
    name: str = Field(min_length=2)
    avatar: Annotated[UploadFile | None, File()] = None
    # <<< FIX: Add 'about' field to the form DTO
    about: Optional[str] = Field(default=None)


class ChangeEmailForm(BaseModel):
    account_password: str
    new_email: EmailStr

    @field_validator("new_email", mode="after")
    @classmethod
    def email_lower(cls, email: str):
        return email.lower()


class ChangePasswordForm(BaseModel):
    account_password: str
    new_password: str = Field(min_length=8)
    password_confirmation: str

    @field_validator("password_confirmation", mode="after")
    @classmethod
    def confirm_password(cls, password_confirmation: str, info: FieldValidationInfo):
        if password_confirmation != info.data.get("new_password"):
            raise ValueError("Password do not match")
        return password_confirmation.lower()