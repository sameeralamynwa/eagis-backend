from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from jinja2 import FileSystemLoader
from sqlalchemy import func, select, or_
from sqlalchemy.orm import selectinload
from apps.auth.dependency import IsUserType
from apps.auth.enums import UserType
from core.db import SessionDependency
from core.jinja.helpers import get_template_rederer
from core.session_helpers import flash
from .dtos import CreateBlogCategoryForm, DeleteBlogCategoryForm, BlogCategorysListQuery
from ..config import get_config
from apps.auth.dependency import AuthDependency
from core.exceptions.common import BadRequestErrorException, NotFoundException
from apps.blogs.models import BlogCategory


router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(IsUserType([UserType.SUPER_ADMIN]))],
)

config = get_config()

render = get_template_rederer(
    FileSystemLoader(str(config.template_path)),
)


@router.get("/", name="admin.blog_categories")
async def get_blog_categories(
    request: Request,
    session: SessionDependency,
    auth: AuthDependency,
    qs: Annotated[BlogCategorysListQuery, Query()],
):
    base_query = select(BlogCategory).options(selectinload(BlogCategory.thumbnail))

    if qs.search:
        base_query = base_query.where(
            or_(
                BlogCategory.name.ilike(f"%{qs.search}%"),
                BlogCategory.slug.ilike(f"%{qs.search}%"),
            )
        )

    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.scalar(count_query)

    paginated_query = base_query.limit(qs.per_page).offset((qs.page - 1) * qs.per_page)

    results = await session.scalars(paginated_query)
    blog_categories = results.all()

    auth_user = await auth.get_user_or_raise()
    delete_form = DeleteBlogCategoryForm(meta={"csrf_context": request.session})
    ctx = dict(
        user=auth_user,
        delete_form=delete_form,
        data=dict(
            data=blog_categories,
            page=qs.page,
            per_page=qs.per_page,
            total=total,
        ),
    )

    return render(request, "admin/blog_categories/index.html.j2", ctx)


@router.api_route(
    "/create",
    methods=["GET", "POST"],
    name="admin.blog_categories.create",
    operation_id="admin_blog_categories_create",
)
async def create_blog_category(
    request: Request,
    auth: AuthDependency,
    session: SessionDependency,
):
    form_data = await request.form()
    form = CreateBlogCategoryForm(form_data, meta={"csrf_context": request.session})

    async def render_template():
        auth_user = await auth.get_user_or_raise()
        ctx = dict(user=auth_user, form=form)
        return render(request, "admin/blog_categories/create.html.j2", ctx)

    if (request.method == "POST") and form.validate():
        exist_name = await session.scalar(
            select(BlogCategory).where(BlogCategory.name == form.name.data)
        )

        if exist_name:
            form.name.errors.append("Name already taken")
            return await render_template()

        exist_slug = await session.scalar(
            select(BlogCategory).where(BlogCategory.slug == form.slug.data)
        )
        if exist_slug:
            form.slug.errors.append("Slug already taken")
            return await render_template()

        blog_category = BlogCategory()
        form.populate_obj(blog_category)
        session.add(blog_category)

        await session.commit()
        flash(request, "BlogCategory Created", "success")
        return RedirectResponse(request.url_for("admin.blog_categories"), 303)

    return await render_template()


@router.api_route(
    "/{id}/edit",
    methods=["GET", "POST"],
    name="admin.blog_categories.edit",
    operation_id="admin_blog_categories_edit",
)
async def edit_blog_category(
    id: int, request: Request, auth: AuthDependency, session: SessionDependency
):
    blog_category = await session.scalar(
        select(BlogCategory).where(BlogCategory.id == id)
    )
    if not blog_category:
        raise NotFoundException()

    if request.method == "POST":
        form_data = await request.form()
        form = CreateBlogCategoryForm(
            form_data, obj=blog_category, meta={"csrf_context": request.session}
        )
    else:
        form = CreateBlogCategoryForm(
            obj=blog_category, meta={"csrf_context": request.session}
        )

    async def render_template():
        auth_user = await auth.get_user_or_raise()
        ctx = dict(user=auth_user, form=form, id=id)
        return render(request, "admin/blog_categories/edit.html.j2", ctx)

    if (request.method == "POST") and form.validate():
        exist_name = await session.scalar(
            select(BlogCategory).where(
                BlogCategory.name == form.name.data, BlogCategory.id != id
            )
        )
        if exist_name:
            form.name.errors.append("Name already taken")
            return await render_template()

        exist_slug = await session.scalar(
            select(BlogCategory).where(
                BlogCategory.slug == form.slug.data, BlogCategory.id != id
            )
        )
        if exist_slug:
            form.slug.errors.append("Slug already taken")
            return await render_template()

        form.populate_obj(blog_category)

        session.add(blog_category)

        await session.commit()
        flash(request, "BlogCategory Updated", "success")
        return RedirectResponse(request.url_for("admin.blog_categories"), 303)

    return await render_template()


@router.delete("/{id}", name="admin.blog_categories.delete")
async def delete_blog_category(id: int, request: Request, session: SessionDependency):
    form_data = await request.form()
    delete_form = DeleteBlogCategoryForm(
        formdata=form_data, meta={"csrf_context": request.session}
    )

    if delete_form.validate():
        blog_category = await session.get_one(BlogCategory, id)
        await session.delete(blog_category)
        await session.commit()
        flash(request, "BlogCategory deleted", "success")
        return RedirectResponse(request.url_for("admin.blog_categories"), 303)
    else:
        raise BadRequestErrorException("Invalid Request")
