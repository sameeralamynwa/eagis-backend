# In apps/auth/routes.py

import random
import string
from datetime import datetime, timedelta, timezone
from typing import Annotated
# Remove Form, Request and HTTPException as they are no longer needed in /login
from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from sqlalchemy import false, select
from core.db import SessionDependency
from .enums import OtpPurpose, UserType
from .models import Otp, Profile, User
from core.responses import SuccessResponse
from .dependency import AuthDependency
# <<< FIX: Import the new LoginForm DTO
from .dtos import UserRegisterForm, ResetPasswordForm, ForgotPasswordForm, ResendVerificationEmailForm, LoginForm
from core.hash import HashUtillsDependency
from apps.mails.dependency import MailServiceDependency
from core import ConfigDepedency as GlobalConfigDependency

auth_router = APIRouter(tags=["Auth"])


@auth_router.post("/login")
async def login(
    # <<< FIX: Expect a JSON body that matches the LoginForm Pydantic model
    form: LoginForm,
    auth: AuthDependency,
):
    print("\n--- [ROUTER] /login endpoint hit (JSON Mode) ---")
    print(f"[ROUTER] Received email: '{form.email}'")
    
    # Pass the email and password from the validated form to the login logic
    token = await auth.oauth_login(form.email, form.password)
    
    print("[ROUTER] Token generation successful.")
    print("--- [ROUTER] /login endpoint finished ---\n")
    return token


# ... (The rest of the file is unchanged) ...
@auth_router.post("/register")
async def register(
    form: UserRegisterForm,
    session: SessionDependency,
    hash_utils: HashUtillsDependency,
    mail_service: MailServiceDependency,
    global_config: GlobalConfigDependency,
) -> SuccessResponse:
    user_email_exist = await session.scalar(
        select(User).where(User.email == form.email)
    )
    if user_email_exist:
        raise RequestValidationError(
            errors=[{"loc": ("body", "email"), "msg": "Email is aleady taken"}]
        )
    username_exist = await session.scalar(
        select(User).where(User.username == form.username)
    )
    if username_exist:
        raise RequestValidationError(
            errors=[{"loc": ("body", "username"), "msg": "Username is aleady taken"}]
        )
    hashed_password = hash_utils.get_hash(form.password)
    otp = "".join(random.choices(string.digits, k=6))
    hashed_otp = hash_utils.get_hash(otp)
    profile = Profile(avatar=None)
    user = User(
        email=form.email,
        name=form.name,
        username=form.username,
        password=hashed_password,
        email_verified=False,
        is_active=True,
        user_type=UserType.User,
        profile=profile,
    )
    db_otp = Otp(
        email=user.email,
        is_used=False,
        otp_hash=hashed_otp,
        purpose=OtpPurpose.VERIFY_EMAIL,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=60),
    )
    session.add(user)
    session.add(profile)
    session.add(db_otp)
    await session.commit()
    mail_data = {
        "app_url": global_config.app_url,
        "app_name": global_config.app_name,
        "data": {"name": user.name, "otp": otp},
    }
    await mail_service.send_mail(
        subject="Verify Your Email - " + global_config.app_name,
        emails=[user.email],
        template_name="mails/verify_email.html",
        data=mail_data,
    )
    return SuccessResponse(detail="Registered Successfully, Please verify your email")


@auth_router.post("/verfiy-email")
async def verify_email(
    email: str, otp: str, session: SessionDependency, hash_utils: HashUtillsDependency
):
    db_otp = await session.scalar(
        select(Otp)
        .where(
            Otp.email == email,
            Otp.purpose == OtpPurpose.VERIFY_EMAIL,
            Otp.is_used == false(),
        )
        .order_by(Otp.created_at.desc())
    )
    if not db_otp:
        raise HTTPException(400, detail="OTP not found")
    if db_otp.expires_at < datetime.now(timezone.utc):
        raise HTTPException(400, detail="OTP expired")
    if not hash_utils.verify_hash(otp, db_otp.otp_hash):
        raise HTTPException(400, detail="Invalid OTP")
    user = await session.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(400, detail="Invalid User email")
    user.email_verified = True
    db_otp.is_used = True
    session.add(user)
    session.add(db_otp)
    await session.commit()
    return SuccessResponse(detail="Email Verified Successfully")


@auth_router.post("/re-verfiy-email")
async def re_verify_email(
    form: ResendVerificationEmailForm,
    session: SessionDependency,
    hash_utils: HashUtillsDependency,
    global_config: GlobalConfigDependency,
    mail_service: MailServiceDependency,
):
    user = await session.scalar(select(User).where(User.email == form.email))
    if not user:
        raise HTTPException(400, detail="Invalid User email")
    otp = "".join(random.choices(string.digits, k=6))
    hashed_otp = hash_utils.get_hash(otp)
    db_otp = Otp(
        email=user.email,
        is_used=False,
        otp_hash=hashed_otp,
        purpose=OtpPurpose.VERIFY_EMAIL,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=60),
    )
    session.add(db_otp)
    await session.commit()
    mail_data = {
        "app_url": global_config.app_url,
        "app_name": global_config.app_name,
        "data": {"name": user.name, "otp": otp},
    }
    await mail_service.send_mail(
        subject="Verify Your Email - " + global_config.app_name,
        emails=[user.email],
        template_name="mails/verify_email.html",
        data=mail_data,
    )
    return SuccessResponse(detail="Verification Email Sent. Please check your inbox")


@auth_router.post("/forgot-password")
async def forgot_password(
    form: ForgotPasswordForm,
    session: SessionDependency,
    hash_utils: HashUtillsDependency,
    global_config: GlobalConfigDependency,
    mail_service: MailServiceDependency,
):
    user = await session.scalar(select(User).where(User.email == form.email))
    if not user:
        return SuccessResponse(detail="If an account with that email exists, a password reset otp has been sent.")
    otp = "".join(random.choices(string.digits, k=6))
    hashed_otp = hash_utils.get_hash(otp)
    db_otp = Otp(
        email=user.email,
        is_used=False,
        otp_hash=hashed_otp,
        purpose=OtpPurpose.RESET_PASSWORD,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    session.add(db_otp)
    await session.commit()
    mail_data = {
        "app_url": global_config.app_url,
        "app_name": global_config.app_name,
        "data": {"name": user.name, "otp": otp},
    }
    await mail_service.send_mail(
        subject="Forgot Password - " + global_config.app_name,
        emails=[user.email],
        template_name="mails/forgot_password.html",
        data=mail_data,
    )
    return SuccessResponse(detail="If an account with that email exists, a password reset otp has been sent.")


@auth_router.post("/reset-password")
async def reset_password(
    form_data: ResetPasswordForm,
    session: SessionDependency,
    hash_utils: HashUtillsDependency,
):
    db_otp = await session.scalar(
        select(Otp)
        .where(
            Otp.email == form_data.email,
            Otp.purpose == OtpPurpose.RESET_PASSWORD,
            Otp.is_used == false(),
        )
        .order_by(Otp.created_at.desc())
    )
    if not db_otp:
        raise HTTPException(400, detail="OTP not found or already used.")
    if db_otp.expires_at < datetime.now(timezone.utc):
        raise HTTPException(400, detail="OTP expired")
    if not hash_utils.verify_hash(form_data.otp, db_otp.otp_hash):
        raise HTTPException(400, detail="Invalid OTP")
    user = await session.scalar(select(User).where(User.email == form_data.email))
    if not user:
        raise HTTPException(400, detail="Invalid User email")
    password_hash = hash_utils.get_hash(form_data.password)
    user.password = password_hash
    db_otp.is_used = True
    session.add(user)
    session.add(db_otp)
    await session.commit()
    return SuccessResponse(detail="Password Changed Successfully")