from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from jinja2 import FileSystemLoader
from sqlalchemy import func, select, or_
from apps.auth.dependency import IsUserType
from apps.auth.enums import UserType
from core.db import SessionDependency
from apps.auth.models import Role
from core.jinja.helpers import get_template_rederer
from core.session_helpers import flash
from .dtos import CreateRoleForm, DeleteRoleForm, RolesListQuery
from ..config import get_config
from apps.auth.dependency import AuthDependency
from core.exceptions.common import BadRequestErrorException, NotFoundException


router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(IsUserType([UserType.SUPER_ADMIN]))],
)

config = get_config()

render = get_template_rederer(
    FileSystemLoader(str(config.template_path)),
)


@router.get("/", name="admin.roles")
async def get_roles(
    request: Request,
    session: SessionDependency,
    auth: AuthDependency,
    qs: Annotated[RolesListQuery, Query()],
):
    base_query = select(Role)

    if qs.search:
        base_query = base_query.where(or_(Role.name.ilike(f"%{qs.search}%")))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.scalar(count_query)

    paginated_query = base_query.limit(qs.per_page).offset((qs.page - 1) * qs.per_page)

    results = await session.scalars(paginated_query)
    roles = results.all()

    auth_user = await auth.get_user_or_raise()
    delete_form = DeleteRoleForm(meta={"csrf_context": request.session})
    ctx = dict(
        user=auth_user,
        delete_form=delete_form,
        data=dict(
            data=roles,
            page=qs.page,
            per_page=qs.per_page,
            total=total,
        ),
    )

    return render(request, "admin/roles/index.html.j2", ctx)


@router.api_route(
    "/create",
    methods=["GET", "POST"],
    name="admin.roles.create",
    operation_id="admin_roles_create",
)
async def create_role(
    request: Request,
    auth: AuthDependency,
    session: SessionDependency,
):
    form_data = await request.form()
    form = CreateRoleForm(form_data, meta={"csrf_context": request.session})

    async def render_template():
        auth_user = await auth.get_user_or_raise()
        ctx = dict(user=auth_user, form=form)
        return render(request, "admin/roles/create.html.j2", ctx)

    if (request.method == "POST") and form.validate():
        name_exist = await session.scalar(
            select(Role).where(Role.name == form.name.data)
        )

        if name_exist:
            form.name.errors.append("Name already taken")
            return await render_template()

        role = Role()
        form.populate_obj(role)

        session.add(role)

        await session.commit()
        flash(request, "Role Created", "success")
        return RedirectResponse(request.url_for("admin.roles"), 303)

    return await render_template()


@router.api_route(
    "/{id}/edit",
    methods=["GET", "POST"],
    name="admin.roles.edit",
    operation_id="admin_roles_edit",
)
async def edit_role(
    id: int, request: Request, auth: AuthDependency, session: SessionDependency
):
    role = await session.scalar(select(Role).where(Role.id == id))
    if not role:
        raise NotFoundException()

    if request.method == "POST":
        form_data = await request.form()
        form = CreateRoleForm(
            form_data, obj=role, meta={"csrf_context": request.session}
        )
    else:
        form = CreateRoleForm(obj=role, meta={"csrf_context": request.session})

    async def render_template():
        auth_user = await auth.get_user_or_raise()
        ctx = dict(user=auth_user, form=form, id=id)
        return render(request, "admin/roles/edit.html.j2", ctx)

    if (request.method == "POST") and form.validate():
        name_exist = await session.scalar(
            select(Role).where(Role.name == form.name.data, Role.id != id)
        )
        if name_exist:
            form.name.errors.append("Name already taken")
            return await render_template()

        form.populate_obj(role)
        session.add(role)

        await session.commit()
        flash(request, "Role Updated", "success")
        return RedirectResponse(request.url_for("admin.roles"), 303)

    return await render_template()


@router.delete("/{id}", name="admin.roles.delete")
async def delete_role(id: int, request: Request, session: SessionDependency):
    form_data = await request.form()
    delete_form = DeleteRoleForm(
        formdata=form_data, meta={"csrf_context": request.session}
    )

    if delete_form.validate():
        role = await session.get_one(Role, id)
        await session.delete(role)
        await session.commit()
        flash(request, "Role deleted", "success")
        return RedirectResponse(request.url_for("admin.roles"), 303)
    else:
        raise BadRequestErrorException("Invalid Request")
