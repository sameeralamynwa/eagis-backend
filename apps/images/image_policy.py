# In apps/images/image_policy.py

from typing import Annotated
from fastapi import Depends
from apps.auth.enums import UserType
from core.exceptions.common import ForbiddenException
from apps.auth.dependency import AuthDependency

from .models import Image


class ImagePolicy:
    def __init__(self, auth: AuthDependency) -> None:
        self.auth = auth

    async def authorize_get_images(self) -> None:
        pass

    async def authorize_create_images(self) -> None:
        await self.auth.get_user_or_raise()

    async def authorize_update_image(self, image: Image) -> None:
        user = await self.auth.get_user_or_raise()

        is_admin = user.user_type in [UserType.Admin, UserType.SUPER_ADMIN]
        is_owner = user.id == image.user_id

        if is_admin or is_owner:
            return  # Authorization successful

        raise ForbiddenException()

    async def authorize_delete_image(self, image: Image) -> None:
        user = await self.auth.get_user_or_raise()

        is_admin = user.user_type in [UserType.Admin, UserType.SUPER_ADMIN]
        is_owner = user.id == image.user_id

        if is_admin or is_owner:
            return

        raise ForbiddenException()


image_policy_dep = Annotated[ImagePolicy, Depends()]