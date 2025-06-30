from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from jinja2 import FileSystemLoader
from sqlalchemy import func, select, or_
from sqlalchemy.orm import selectinload
from apps.auth.dependency import IsUserType
from apps.auth.enums import UserType
from core.db import SessionDependency
from apps.auth.models import Profile, Role, User
from core.jinja.helpers import get_template_rederer
from core.session_helpers import flash
from apps.auth.dependency import hasPermission # <-- Add this import at the top
from apps.auth.enums import Permissions # <-- Add this import at the top
from .dtos import CreateUserForm, DeleteUserForm, UserListQuery, UpdateUserForm
from ..config import get_config
from apps.auth.dependency import AuthDependency
from core.exceptions.common import BadRequestErrorException, NotFoundException
from core.hash import HashUtillsDependency


router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(IsUserType([UserType.SUPER_ADMIN]))],
)

config = get_config()

render = get_template_rederer(
    FileSystemLoader(str(config.template_path)),
)


@router.get("/", name="admin.users")
async def get_users(
    request: Request,
    session: SessionDependency,
    auth: AuthDependency,
    qs: Annotated[UserListQuery, Query()],
):
    base_query = select(User).options(selectinload(User.roles))

    if qs.search:
        base_query = base_query.where(
            or_(
                User.name.ilike(f"%{qs.search}%"), User.username.ilike(f"%{qs.search}%")
            )
        )

    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.scalar(count_query)

    paginated_query = base_query.limit(qs.per_page).offset((qs.page - 1) * qs.per_page)

    results = await session.scalars(paginated_query)
    users = results.all()

    auth_user = await auth.get_user_or_raise()
    delete_form = DeleteUserForm(meta={"csrf_context": request.session})
    ctx = dict(
        user=auth_user,
        delete_form=delete_form,
        data=dict(
            data=users,
            page=qs.page,
            per_page=qs.per_page,
            total=total,
        ),
    )

    return render(request, "admin/users/index.html.j2", ctx)


@router.api_route(
    "/create",
    methods=["GET", "POST"],
    name="admin.users.create",
    operation_id="admin_users_create",
    dependencies=[Depends(hasPermission(Permissions.MANAGE_USERS))]
)
async def create_user(
    request: Request,
    auth: AuthDependency,
    session: SessionDependency,
    hash_utils: HashUtillsDependency,
):
    form_data = await request.form()
    form = CreateUserForm(form_data, meta={"csrf_context": request.session})
    roles = await session.scalars(select(Role))
    form.role_ids.choices = [(role.id, role.name) for role in roles]

    async def render_template():
        auth_user = await auth.get_user_or_raise()
        ctx = dict(user=auth_user, form=form)
        return render(request, "admin/users/create.html.j2", ctx)

    if (request.method == "POST") and form.validate():
        email_exist = await session.scalar(
            select(User).where(User.email == form.email.data)
        )
        if email_exist:
            form.email.errors.append("Email already taken")
            return await render_template()

        username_exist = await session.scalar(
            select(User).where(User.username == form.username.data)
        )
        if username_exist:
            form.username.errors.append("Username already taken")
            return await render_template()

        user = User()
        form.populate_obj(user)
        user.password = hash_utils.get_hash(form.password.data)

        roles = await session.scalars(
            select(Role).where(Role.id.in_(form.role_ids.data))
        )
        profile = Profile(avatar=None)

        user.roles = list(roles.all())
        user.profile = profile
        session.add(user)
        session.add(profile)

        await session.commit()
        flash(request, "User Created", "success")
        return RedirectResponse(request.url_for("admin.users"), 303)

    return await render_template()


@router.api_route(
    "/{id}/edit",
    methods=["GET", "POST"],
    name="admin.users.edit",
    operation_id="admin_users_edit",
    dependencies=[Depends(hasPermission(Permissions.MANAGE_USERS))]
)
async def edit_user(
    id: int, request: Request, auth: AuthDependency, session: SessionDependency
):
    user = await session.scalar(
        select(User).where(User.id == id).options(selectinload(User.roles))
    )
    if not user:
        raise NotFoundException()

    roles = await session.scalars(select(Role))
    role_choices = [(role.id, role.name) for role in roles]
    if request.method == "POST":
        form_data = await request.form()
        form = UpdateUserForm(
            form_data, obj=user, meta={"csrf_context": request.session}
        )
        form.role_ids.choices = role_choices
    else:
        form = UpdateUserForm(obj=user, meta={"csrf_context": request.session})
        form.role_ids.choices = role_choices
        form.role_ids.data = [role.id for role in user.roles]

    async def render_template():
        auth_user = await auth.get_user_or_raise()
        ctx = dict(user=auth_user, form=form, id=id)
        return render(request, "admin/users/edit.html.j2", ctx)

    if (request.method == "POST") and form.validate():
        email_exist = await session.scalar(
            select(User).where(User.email == form.email.data, User.id != id)
        )
        if email_exist:
            form.email.errors.append("Email already taken")
            return await render_template()

        username_exist = await session.scalar(
            select(User).where(User.username == form.username.data, User.id != id)
        )
        if username_exist:
            form.username.errors.append("Username already taken")
            return await render_template()

        form.populate_obj(user)

        roles = await session.scalars(
            select(Role).where(Role.id.in_(form.role_ids.data))
        )
        user.roles = list(roles.all())
        session.add(user)

        await session.commit()
        flash(request, "User Updated", "success")
        return RedirectResponse(request.url_for("admin.users"), 303)

    return await render_template()


@router.delete("/{id}", name="admin.users.delete", dependencies=[Depends(hasPermission(Permissions.MANAGE_USERS))])
async def delete_user(id: int, request: Request, session: SessionDependency):
    form_data = await request.form()
    delete_form = DeleteUserForm(
        formdata=form_data, meta={"csrf_context": request.session}
    )

    if delete_form.validate():
        user = await session.get_one(User, id)
        await session.delete(user)
        await session.commit()
        flash(request, "User deleted", "success")
        return RedirectResponse(request.url_for("admin.users"), 303)
    else:
        raise BadRequestErrorException("Invalid Request")
