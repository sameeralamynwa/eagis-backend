# In apps/blogs/routes.py

from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from core.exceptions.common import FieldValidationError, NotFoundException
from .models import Blog, BlogCategory
from .blog_policy import BlogPolicyDependency
from .blog_category_policy import BlogCategoryPolicyDependency
from .dtos import (
    BlogCategoryCreate,
    BlogCategoryListQuery,
    BlogCategoryListResponse,
    BlogCategoryRead,
    BlogCategoryUpdate,
    BlogCreate,
    BlogListQuery,
    BlogListResponse,
    BlogRead,
    BlogUpdate,
)
from core.db import SessionDependency
# New Imports needed for the fix
from apps.auth.dependency import AuthDependency
from apps.auth.enums import UserType


blog_router = APIRouter(tags=["Blogs"], prefix="/blogs")
blog_category_router = APIRouter(tags=["Blogs"], prefix="/blog_categories")


@blog_router.get("/", response_model=BlogListResponse)
async def get_blogs(
    qs: Annotated[BlogListQuery, Query()],
    session: SessionDependency,
    # CORRECTED: Removed the incorrect default value.
    auth: AuthDependency,
):
    base_query = select(Blog)

    # Check if the current user is an admin or super admin
    user = await auth.get_user()
    is_admin = user and user.user_type in [UserType.Admin, UserType.SUPER_ADMIN]

    # If the user is NOT an admin, only show published blogs
    if not is_admin:
        base_query = base_query.where(Blog.is_published == True)

    if qs.search:
        base_query = base_query.where(Blog.title.ilike(f"%{qs.search}%"))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.scalar(count_query)

    paginated_query = base_query.limit(qs.per_page).offset((qs.page - 1) * qs.per_page)

    results = await session.scalars(paginated_query)
    blogs = results.all()

    response = {
        "data": blogs,
        "page": qs.page,
        "per_page": qs.per_page,
        "total": total,
    }
    return response


@blog_router.get("/{slug}", response_model=BlogRead)
async def get_blog(
    slug: str,
    session: SessionDependency,
    # CORRECTED: Removed the incorrect default value.
    auth: AuthDependency,
):
    blog = await session.scalar(select(Blog).where(Blog.slug == slug))

    if not blog:
        raise NotFoundException()

    # Check if the current user is an admin or super admin
    user = await auth.get_user()
    is_admin = user and user.user_type in [UserType.Admin, UserType.SUPER_ADMIN]

    # If the blog is not published AND the user is not an admin, hide it
    if not blog.is_published and not is_admin:
        raise NotFoundException()

    return blog


@blog_category_router.get("/", response_model=BlogCategoryListResponse)
async def get_categories(
    qs: Annotated[BlogCategoryListQuery, Query()],
    session: SessionDependency,
    # CORRECTED: Removed the incorrect default value.
    auth: AuthDependency,
):
    base_query = select(BlogCategory)

    user = await auth.get_user()
    is_admin = user and user.user_type in [UserType.Admin, UserType.SUPER_ADMIN]

    # If the user is NOT an admin, only show published categories
    if not is_admin:
        base_query = base_query.where(BlogCategory.is_published == True)

    if qs.search:
        base_query = base_query.where(BlogCategory.name.ilike(f"%{qs.search}%"))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.scalar(count_query)

    paginated_query = base_query.limit(qs.per_page).offset((qs.page - 1) * qs.per_page)
    results = await session.scalars(paginated_query)
    categories = results.all()

    response = {
        "data": categories,
        "page": qs.page,
        "per_page": qs.per_page,
        "total": total,
    }
    return response


@blog_category_router.get("/{slug}", response_model=BlogCategoryRead)
async def get_blog_category(
    slug: str,
    session: SessionDependency,
    # CORRECTED: Removed the incorrect default value.
    auth: AuthDependency,
):
    category = await session.scalar(select(BlogCategory).where(BlogCategory.slug == slug))

    if not category:
        raise NotFoundException()

    user = await auth.get_user()
    is_admin = user and user.user_type in [UserType.Admin, UserType.SUPER_ADMIN]

    # If the category is not published AND the user is not an admin, hide it
    if not category.is_published and not is_admin:
        raise NotFoundException()
        
    return category

# --- The Create, Update, and Delete routes below are unchanged ---

@blog_router.post("/", response_model=BlogRead, status_code=201)
async def create_blog(
    form_data: BlogCreate,
    session: SessionDependency,
    blog_policy: BlogPolicyDependency,
):
    await blog_policy.authorize_create_blogs()
    slug_exist = await session.scalar(select(Blog).where(Blog.slug == form_data.slug))

    if slug_exist:
        raise FieldValidationError("body", field_name="slug", msg="Slug Already taken")

    blog = Blog(**form_data.model_dump())

    session.add(blog)
    await session.commit()
    await session.refresh(blog)
    return blog


@blog_router.put("/{slug}", response_model=BlogRead)
async def update_blog(
    slug: str,
    form_data: BlogUpdate,
    session: SessionDependency,
    blog_policy: BlogPolicyDependency,
):
    await blog_policy.authorize_update_blogs()
    blog = await session.scalar(select(Blog).where(Blog.slug == slug))

    if not blog:
        raise NotFoundException()

    changed_slug_exist = await session.scalar(
        select(Blog).where(Blog.slug == form_data.slug, Blog.id != blog.id)
    )

    if changed_slug_exist:
        raise FieldValidationError("body", field_name="slug", msg="Slug Already taken")

    data = form_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(blog, key, value)

    session.add(blog)
    await session.commit()
    await session.refresh(blog)
    return blog


@blog_router.delete("/{slug}", status_code=204)
async def delete_blog(
    slug: str,
    session: SessionDependency,
    blog_policy: BlogPolicyDependency,
):
    await blog_policy.authorize_delete_blogs()
    blog = await session.scalar(select(Blog).where(Blog.slug == slug))

    if not blog:
        raise NotFoundException()

    await session.delete(blog)
    await session.commit()
    return None


@blog_category_router.post("/", response_model=BlogCategoryRead, status_code=201)
async def create_blog_category(
    form_data: BlogCategoryCreate,
    session: SessionDependency,
    blog_category_policy: BlogCategoryPolicyDependency,
):
    await blog_category_policy.authorize_create_blog_category()
    slug_exist = await session.scalar(
        select(BlogCategory).where(BlogCategory.slug == form_data.slug)
    )

    if slug_exist:
        raise FieldValidationError("body", field_name="slug", msg="Slug Already taken")

    category = BlogCategory(**form_data.model_dump())

    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


@blog_category_router.put("/{slug}", response_model=BlogCategoryRead)
async def update_blog_category(
    slug: str,
    form_data: BlogCategoryUpdate,
    session: SessionDependency,
    blog_category_policy: BlogCategoryPolicyDependency,
):
    await blog_category_policy.authorize_update_blog_category()
    category = await session.scalar(select(BlogCategory).where(BlogCategory.slug == slug))

    if not category:
        raise NotFoundException()

    changed_slug_exist = await session.scalar(
        select(BlogCategory).where(
            BlogCategory.slug == form_data.slug, BlogCategory.id != category.id
        )
    )

    if changed_slug_exist:
        raise FieldValidationError("body", field_name="slug", msg="Slug Already taken")

    data = form_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(category, key, value)

    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


@blog_category_router.delete("/{slug}", status_code=204)
async def delete_blog_category(
    slug: str,
    session: SessionDependency,
    blog_category_policy: BlogCategoryPolicyDependency,
):
    await blog_category_policy.authorize_delete_blog_category()
    category = await session.scalar(select(BlogCategory).where(BlogCategory.slug == slug))

    if not category:
        raise NotFoundException()

    await session.delete(category)
    await session.commit()
    return None