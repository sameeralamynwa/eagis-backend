# apps/account/account_policy.py

from typing import Annotated
from fastapi import Depends
from core.exceptions.common import ForbiddenException
from apps.auth.dependency import AuthDependency
from core.hash import HashUtillsDependency


class AccountPolicy:
    def __init__(self, auth: AuthDependency, hash_utils: HashUtillsDependency) -> None:
        self.auth = auth
        self.hash_utils = hash_utils

    async def authorize_get_my_account(self) -> None:
        await self.auth.get_user_or_raise()

    async def authorize_update_account_detail(self) -> None:
        await self.auth.get_user_or_raise()

    async def authorize_change_email(self, account_password: str) -> None:
        user = await self.auth.get_user_or_raise()
        if not self.hash_utils.verify_hash(account_password, user.password):
            raise ForbiddenException()

    async def authorize_change_password(self, account_password: str) -> None:
        user = await self.auth.get_user_or_raise()
        if not self.hash_utils.verify_hash(account_password, user.password):
            raise ForbiddenException()


account_policy_dep = Annotated[AccountPolicy, Depends()]
