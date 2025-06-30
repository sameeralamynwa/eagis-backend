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
from .dtos import CreateBlogForm, DeleteBlogForm, BlogsListQuery
from ..config import get_config
from apps.auth.dependency import AuthDependency
from core.exceptions.common import BadRequestErrorException, NotFoundException
from apps.blogs.models import Blog, BlogCategory


router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(IsUserType([UserType.SUPER_ADMIN]))],
)

config = get_config()

render = get_template_rederer(
    FileSystemLoader(str(config.template_path)),
)


@router.get("/", name="admin.blogs")
async def get_blogs(
    request: Request,
    session: SessionDependency,
    auth: AuthDependency,
    qs: Annotated[BlogsListQuery, Query()],
):
    base_query = select(Blog).options(
        selectinload(Blog.thumbnail), selectinload(Blog.category)
    )

    if qs.search:
        base_query = base_query.where(
            or_(
                Blog.title.ilike(f"%{qs.search}%"),
                Blog.slug.ilike(f"%{qs.search}%"),
            )
        )

    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.scalar(count_query)

    paginated_query = base_query.limit(qs.per_page).offset((qs.page - 1) * qs.per_page)

    results = await session.scalars(paginated_query)
    blogs = results.all()

    auth_user = await auth.get_user_or_raise()
    delete_form = DeleteBlogForm(meta={"csrf_context": request.session})
    ctx = dict(
        user=auth_user,
        delete_form=delete_form,
        data=dict(
            data=blogs,
            page=qs.page,
            per_page=qs.per_page,
            total=total,
        ),
    )

    return render(request, "admin/blogs/index.html.j2", ctx)


@router.api_route(
    "/create",
    methods=["GET", "POST"],
    name="admin.blogs.create",
    operation_id="admin_blogs_create",
)
async def create_blog(
    request: Request,
    auth: AuthDependency,
    session: SessionDependency,
):
    form_data = await request.form()
    form = CreateBlogForm(form_data, meta={"csrf_context": request.session})
    categories = await session.scalars(select(BlogCategory))
    category_choices = [(category.id, category.name) for category in categories]
    form.category_id.choices = category_choices

    async def render_template():
        auth_user = await auth.get_user_or_raise()
        ctx = dict(user=auth_user, form=form)
        return render(request, "admin/blogs/create.html.j2", ctx)

    if (request.method == "POST") and form.validate():
        exist_title = await session.scalar(
            select(Blog).where(Blog.title == form.title.data)
        )

        if exist_title:
            form.name.errors.append("Title already taken")
            return await render_template()

        exist_slug = await session.scalar(
            select(Blog).where(Blog.slug == form.slug.data)
        )
        if exist_slug:
            form.slug.errors.append("Slug already taken")
            return await render_template()

        blog = Blog()
        form.populate_obj(blog)
        session.add(blog)

        await session.commit()
        flash(request, "Blog Created", "success")
        return RedirectResponse(request.url_for("admin.blogs"), 303)

    return await render_template()


@router.api_route(
    "/{id}/edit",
    methods=["GET", "POST"],
    name="admin.blogs.edit",
    operation_id="admin_blogs_edit",
)
async def edit_blog(
    id: int, request: Request, auth: AuthDependency, session: SessionDependency
):
    blog = await session.scalar(select(Blog).where(Blog.id == id))
    if not blog:
        raise NotFoundException()

    if request.method == "POST":
        form_data = await request.form()
        form = CreateBlogForm(
            form_data, obj=blog, meta={"csrf_context": request.session}
        )
    else:
        form = CreateBlogForm(obj=blog, meta={"csrf_context": request.session})

    categories = await session.scalars(select(BlogCategory))
    category_choices = [(category.id, category.name) for category in categories]
    form.category_id.choices = category_choices

    async def render_template():
        auth_user = await auth.get_user_or_raise()
        ctx = dict(user=auth_user, form=form, id=id)
        return render(request, "admin/blogs/edit.html.j2", ctx)

    if (request.method == "POST") and form.validate():
        exist_title = await session.scalar(
            select(Blog).where(Blog.title == form.title.data, Blog.id != id)
        )
        if exist_title:
            form.name.errors.append("Title already taken")
            return await render_template()

        exist_slug = await session.scalar(
            select(Blog).where(Blog.slug == form.slug.data, Blog.id != id)
        )
        if exist_slug:
            form.slug.errors.append("Slug already taken")
            return await render_template()

        form.populate_obj(blog)

        session.add(blog)

        await session.commit()
        flash(request, "Blog Updated", "success")
        return RedirectResponse(request.url_for("admin.blogs"), 303)

    return await render_template()


@router.delete("/{id}", name="admin.blogs.delete")
async def delete_blog(id: int, request: Request, session: SessionDependency):
    form_data = await request.form()
    delete_form = DeleteBlogForm(
        formdata=form_data, meta={"csrf_context": request.session}
    )

    if delete_form.validate():
        blog = await session.get_one(Blog, id)
        await session.delete(blog)
        await session.commit()
        flash(request, "Blog deleted", "success")
        return RedirectResponse(request.url_for("admin.blogs"), 303)
    else:
        raise BadRequestErrorException("Invalid Request")
