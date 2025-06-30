from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic import ConfigDict


class UserRead(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    user_type: str 
    model_config = ConfigDict(from_attributes=True)


class LoginForm(BaseModel):
    email: EmailStr
    password: str


class UserRegisterForm(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]
    password_confirmation: Annotated[str, Field(min_length=1)]

    @field_validator("password_confirmation", mode="after")
    @classmethod
    def confirm_password(cls, password_confirmation: str, info: FieldValidationInfo):
        if password_confirmation != info.data.get("password"):
            raise ValueError("Password do not match")
        return password_confirmation

    @field_validator("email", mode="after")
    @classmethod
    def email_lower(cls, email: str):
        return email.lower()


class ResetPasswordForm(BaseModel):
    otp: str
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]
    password_confirmation: Annotated[str, Field(min_length=1)]

    @field_validator("password_confirmation", mode="after")
    @classmethod
    def confirm_password(cls, password_confirmation: str, info: FieldValidationInfo):
        if password_confirmation != info.data.get("password"):
            raise ValueError("Password do not match")
        return password_confirmation

    @field_validator("email", mode="after")
    @classmethod
    def email_lower(cls, email: str):
        return email.lower()


class ForgotPasswordForm(BaseModel):
    email: EmailStr


class ResendVerificationEmailForm(BaseModel):
    email: EmailStr