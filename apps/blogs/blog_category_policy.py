# In apps/blogs/blog_category_policy.py

from typing import Annotated
from fastapi import Depends
from apps.auth.dependency import AuthDependency, hasPermission
from apps.auth.enums import Permissions


class BlogCategoryPolicy:
    def __init__(self, auth: AuthDependency) -> None:
        self.auth = auth

    async def authorize_get_blog_categories(self) -> None:
        pass

    async def authorize_get_blog_category(self) -> None:
        pass
    
    async def authorize_create_blog_category(self) -> None:
        checker = hasPermission(Permissions.MANAGE_BLOGS)
        await checker(self.auth)

    async def authorize_update_blog_category(self) -> None:
        checker = hasPermission(Permissions.MANAGE_BLOGS)
        await checker(self.auth)

    async def authorize_delete_blog_category(self) -> None:
        checker = hasPermission(Permissions.MANAGE_BLOGS)
        await checker(self.auth)


BlogCategoryPolicyDependency = Annotated[BlogCategoryPolicy, Depends()]