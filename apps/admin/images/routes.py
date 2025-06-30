from typing import Annotated
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import RedirectResponse
from jinja2 import FileSystemLoader
from sqlalchemy import func, select, or_
from apps.auth.dependency import IsUserType
from core.drive.abstracts import UploadFileOptions
from core.drive.base import DriveDependency
from apps.auth.enums import UserType
from core.db import SessionDependency
from apps.images.models import Image
from core.jinja.helpers import get_template_rederer
from core.session_helpers import flash
from .dtos import CreateImageForm, DeleteImageForm, ImagesListQuery
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

image_upload_options = UploadFileOptions(
    allowed_types=["image/jpg", "image/jpeg", "image/webp", "image/png"],
    max_size_bytes=1024 * 1024 * 5,  # 5mb
)


@router.get("/", name="admin.images")
async def get_images(
    request: Request,
    session: SessionDependency,
    auth: AuthDependency,
    qs: Annotated[ImagesListQuery, Query()],
):
    base_query = select(Image)

    if qs.search:
        base_query = base_query.where(or_(Image.title.ilike(f"%{qs.search}%")))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.scalar(count_query)

    paginated_query = base_query.limit(qs.per_page).offset((qs.page - 1) * qs.per_page)

    results = await session.scalars(paginated_query)
    images = results.all()

    auth_user = await auth.get_user_or_raise()
    delete_form = DeleteImageForm(meta={"csrf_context": request.session})
    ctx = dict(
        user=auth_user,
        delete_form=delete_form,
        data=dict(
            data=images,
            page=qs.page,
            per_page=qs.per_page,
            total=total,
        ),
    )

    return render(request, "admin/images/index.html.j2", ctx)


@router.get(
    "/create",
    name="admin.images.create",
)
async def create_image(
    request: Request,
    auth: AuthDependency,
):
    form_data = await request.form()
    form = CreateImageForm(form_data, meta={"csrf_context": request.session})
    auth_user = await auth.get_user_or_raise()

    async def render_template():
        ctx = dict(user=auth_user, form=form)
        return render(request, "admin/images/create.html.j2", ctx)

    return await render_template()


@router.post(
    "/store",
    name="admin.images.store",
)
async def store_image(
    request: Request,
    file: Annotated[UploadFile, File()],
    auth: AuthDependency,
    session: SessionDependency,
    drive: DriveDependency,
):
    form_data = await request.form()
    form = CreateImageForm(form_data, meta={"csrf_context": request.session})
    auth_user = await auth.get_user_or_raise()

    async def render_template():
        ctx = dict(user=auth_user, form=form)
        return render(request, "admin/images/create.html.j2", ctx)

    if form.validate():
        image = Image()
        form.populate_obj(image)
        image.uploaded_by = auth_user

        try:
            url = await drive.upload_file(file, image_upload_options)
            image.url = url
        except HTTPException as e:
            flash(request, "File Error - " + e.detail, "error")
            return await render_template()

        session.add(image)

        await session.commit()
        flash(request, "Image Created", "success")
        return RedirectResponse(request.url_for("admin.images"), 303)

    return await render_template()


@router.api_route(
    "/{id}/edit",
    methods=["GET", "POST"],
    name="admin.images.edit",
    operation_id="admin_users_edit",
)
async def edit_image(
    id: int, request: Request, auth: AuthDependency, session: SessionDependency
):
    image = await session.scalar(select(Image).where(Image.id == id))
    if not image:
        raise NotFoundException()

    if request.method == "POST":
        form_data = await request.form()
        form = CreateImageForm(
            form_data, obj=image, meta={"csrf_context": request.session}
        )
    else:
        form = CreateImageForm(obj=image, meta={"csrf_context": request.session})

    async def render_template():
        auth_user = await auth.get_user_or_raise()
        ctx = dict(user=auth_user, form=form, id=id)
        return render(request, "admin/images/edit.html.j2", ctx)

    if (request.method == "POST") and form.validate():
        form.populate_obj(image)
        session.add(image)

        await session.commit()
        flash(request, "Image Updated", "success")
        return RedirectResponse(request.url_for("admin.images"), 303)

    return await render_template()


@router.delete("/{id}", name="admin.images.delete")
async def delete_image(
    id: int,
    request: Request,
    session: SessionDependency,
    drive: DriveDependency,
):
    form_data = await request.form()
    delete_form = DeleteImageForm(
        formdata=form_data, meta={"csrf_context": request.session}
    )

    if delete_form.validate():
        image = await session.get_one(Image, id)
        await session.delete(image)
        await session.commit()
        await drive.delete_file(image.url)
        flash(request, "Image deleted", "success")
        return RedirectResponse(request.url_for("admin.images"), 303)
    else:
        raise BadRequestErrorException("Invalid Request")
