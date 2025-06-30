from datetime import datetime
from typing import Annotated
from fastapi import File, UploadFile
from pydantic import BaseModel
from core.dtos import PaginationQuery
from core.responses import PaginatedResponse


class ImageListQuery(PaginationQuery):
    search: str | None = None


class RelatedUser(BaseModel):
    id: int
    name: str


class ImageRead(BaseModel):
    id: int
    url: str
    alt_text: str | None
    title: str | None
    user_id: int
    created_at: datetime
    created_at: datetime
    uploaded_by: RelatedUser


class ImageListResponse(PaginatedResponse):
    data: list[ImageRead] = []


class ImageCreate(BaseModel):
    alt_text: str | None
    title: str | None
    file: Annotated[UploadFile, File()]


class ImageUpdate(BaseModel):
    alt_text: str | None
    title: str | None
