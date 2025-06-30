# In apps/account/routes.py

from datetime import datetime, timedelta, timezone
import random
import string
from typing import Annotated, Optional
# Import Depends, Form, File, and UploadFile
from fastapi import APIRouter, Depends, Form, File, UploadFile
from apps.auth.enums import OtpPurpose
from apps.auth.models import Otp
from core.drive.abstracts import UploadFileOptions
from .dtos import (
    AccountDetailRead,
    ChangeEmailForm,
    ChangePasswordForm,
)
from core.exceptions.common import BadRequestErrorException
from .account_policy import account_policy_dep
from core.db import SessionDependency
from apps.auth.dependency import AuthDependency
from core.drive import DriveDependency
from apps.mails.dependency import MailServiceDependency
from core.hash import HashUtillsDependency
from core import ConfigDepedency as GlobalConfigDependency


account_router = APIRouter(tags=["Profile"], prefix="/account")
image_upload_options = UploadFileOptions(
    allowed_types=["image/jpg", "image/jpeg", "image/webp", "image/png"],
    max_size_bytes=1024 * 1024 * 5,  # 5mb
)


@account_router.get("/me", response_model=AccountDetailRead)
async def get_my_detail(
    session: SessionDependency, account_policy: account_policy_dep, auth: AuthDependency
):
    await account_policy.authorize_get_my_account()
    current_user = await auth.get_user_or_raise()
    await session.refresh(current_user, attribute_names=["profile"])
    return current_user


@account_router.put("/update", response_model=AccountDetailRead)
async def update_account_detail(
    name: Annotated[str, Form()],
    session: SessionDependency,
    account_policy: account_policy_dep,
    auth: AuthDependency,
    drive: DriveDependency,
    about: Annotated[Optional[str], Form()] = None,
    avatar: Annotated[Optional[UploadFile], File()] = None,
):
    await account_policy.authorize_update_account_detail()
    current_user = await auth.get_user_or_raise()
    await session.refresh(current_user, attribute_names=["profile"])

    # Use the arguments directly
    current_user.name = name
    if about is not None:
        current_user.profile.about = about
        
    if avatar:
        uploaded_avatar_url = await drive.upload_file(avatar, image_upload_options)
        current_user.profile.avatar = uploaded_avatar_url

    session.add(current_user)
    session.add(current_user.profile)
    await session.commit()
    await session.refresh(current_user, attribute_names=["profile", "updated_at"])

    return current_user


@account_router.put("/change-email", response_model=AccountDetailRead)
async def change_email(
    session: SessionDependency,
    account_policy: account_policy_dep,
    auth: AuthDependency,
    form_data: ChangeEmailForm,
    mail_service: MailServiceDependency,
    global_config: GlobalConfigDependency,
    hash_utils: HashUtillsDependency,
):
    await account_policy.authorize_change_email(form_data.account_password)
    current_user = await auth.get_user_or_raise()
    if form_data.new_email == current_user.email:
        raise BadRequestErrorException("Email not changed! Please provide new email")

    current_user.email = form_data.new_email
    current_user.email_verified = False
    session.add(current_user)

    otp = "".join(random.choices(string.digits, k=6))
    hashed_otp = hash_utils.get_hash(otp)
    db_otp = Otp(
        email=current_user.email,
        is_used=False,
        otp_hash=hashed_otp,
        purpose=OtpPurpose.VERIFY_EMAIL,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=60),
    )
    session.add(db_otp)
    await session.commit()
    await session.refresh(current_user)
    await session.refresh(current_user, attribute_names=["profile"])

    mail_data = {
        "app_url": global_config.app_url,
        "app_name": global_config.app_name,
        "data": {"name": current_user.name, "otp": otp},
    }
    await mail_service.send_mail(
        subject="Verify Your Email - " + global_config.app_name,
        emails=[current_user.email],
        template_name="mails/verify_email.html",
        data=mail_data,
    )
    return current_user


@account_router.put("/change-password", response_model=AccountDetailRead)
async def change_password(
    session: SessionDependency,
    account_policy: account_policy_dep,
    auth: AuthDependency,
    form_data: ChangePasswordForm,
    hash_utils: HashUtillsDependency,
):
    await account_policy.authorize_change_password(form_data.account_password)
    current_user = await auth.get_user_or_raise()
    current_user.password = hash_utils.get_hash(form_data.new_password)
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    await session.refresh(current_user, attribute_names=["profile"])
    return current_user