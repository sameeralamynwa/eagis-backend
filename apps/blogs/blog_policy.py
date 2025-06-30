# In apps/blogs/blog_policy.py

from typing import Annotated
from fastapi import Depends
from apps.auth.dependency import AuthDependency, hasPermission
from apps.auth.enums import Permissions


class BlogPolicy:
    def __init__(self, auth: AuthDependency) -> None:
        self.auth = auth

    async def authorize_get_blogs(self) -> None:
        pass

    async def authorize_get_blog(self) -> None:
        pass

    async def authorize_create_blogs(self) -> None:
        checker = hasPermission(Permissions.MANAGE_BLOGS)
        await checker(self.auth)

    async def authorize_update_blogs(self) -> None:
        checker = hasPermission(Permissions.MANAGE_BLOGS)
        await checker(self.auth)

    async def authorize_delete_blogs(self) -> None:
        checker = hasPermission(Permissions.MANAGE_BLOGS)
        await checker(self.auth)


BlogPolicyDependency = Annotated[BlogPolicy, Depends()]