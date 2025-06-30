# In apps/images/routes.py

from typing import Annotated
from sqlalchemy import func, select
from fastapi import APIRouter, Query, Form, HTTPException
from core.db import SessionDependency
from core.exceptions.common import FieldValidationError
from .models import Image
from apps.auth.models import User
from .dtos import (
    ImageListQuery,
    ImageListResponse,
    ImageRead,
    ImageCreate,
    ImageUpdate,
)
from sqlalchemy.orm import selectinload
from core.drive import DriveDependency
from core.drive.abstracts import UploadFileOptions
from .image_policy import image_policy_dep


image_router = APIRouter(tags=["Images"], prefix="/images")
image_upload_options = UploadFileOptions(
    allowed_types=["image/jpg", "image/jpeg", "image/webp", "image/png"],
    max_size_bytes=1024 * 1024 * 5,  # 5mb
)


@image_router.get("/", response_model=ImageListResponse)
async def get_images(
    qs: Annotated[ImageListQuery, Query()],
    session: SessionDependency,
    image_policy: image_policy_dep,
):
    await image_policy.authorize_get_images()
    base_query = select(Image).options(
        selectinload(Image.uploaded_by).selectinload(User.profile)
    )
    if qs.search:
        base_query = base_query.where(Image.title.ilike(f"%{qs.search}%"))
    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.scalar(count_query)
    paginated_query = base_query.limit(qs.per_page).offset((qs.page - 1) * qs.per_page)
    results = await session.scalars(paginated_query)
    images = results.all()
    response = {
        "data": images,
        "page": qs.page,
        "per_page": qs.per_page,
        "total": total,
    }
    return response


@image_router.post("/", response_model=ImageRead, status_code=201)
async def create_image(
    form_data: Annotated[ImageCreate, Form(media_type="multipart/form-data")],
    session: SessionDependency,
    drive: DriveDependency,
    image_policy: image_policy_dep,
):
    await image_policy.authorize_create_images()
    auth_user = await image_policy.auth.get_user_or_raise()
    try:
        url = await drive.upload_file(form_data.file, image_upload_options)
    except HTTPException as e:
        if e.status_code == 400:
            raise FieldValidationError("body", "file", e.detail)
        else:
            raise e
    image = Image(
        **form_data.model_dump(exclude={"file"}),
        user_id=auth_user.id,
        url=url
    )
    session.add(image)
    await session.commit()
    await session.refresh(image, ["uploaded_by"])
    return image


@image_router.put("/{id}", response_model=ImageRead)
async def update_image(
    id: int,
    form_data: ImageUpdate,
    session: SessionDependency,
    image_policy: image_policy_dep,
):
    image = await session.scalar(select(Image).where(Image.id == id))
    if not image:
        raise HTTPException(404, detail="Record Not found")

    # <<< FIX: Authorize the action AFTER getting the image object
    await image_policy.authorize_update_image(image)

    image.alt_text = form_data.alt_text
    image.title = form_data.title
    session.add(image)
    await session.commit()
    await session.refresh(image, ["uploaded_by"])
    return image


@image_router.delete("/{id}", response_model=ImageRead)
async def delete_image(
    id: int,
    session: SessionDependency,
    drive: DriveDependency,
    image_policy: image_policy_dep,
):
    image = await session.scalar(
        select(Image).where(Image.id == id).options(selectinload(Image.uploaded_by))
    )
    if not image:
        raise HTTPException(404, detail="Record Not found")

    await image_policy.authorize_delete_image(image)

    file_url_to_delete = image.url
    
    await session.delete(image)
    await session.commit()
    await drive.delete_file(file_url=file_url_to_delete)

    return image