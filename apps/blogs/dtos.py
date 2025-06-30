from datetime import datetime
from pydantic import BaseModel, field_validator
from core.dtos import PaginationQuery
from core.responses import PaginatedResponse
import re

SLUG_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class BlogListQuery(PaginationQuery):
    search: str | None = None


class RelatedCategory(BaseModel):
    id: int
    name: str


class RelatedThumbnail(BaseModel):
    id: int
    url: str


class BlogRead(BaseModel):
    id: int
    slug: str
    title: str
    is_published: bool
    short_desc: str | None = None
    created_at: datetime
    updated_at_at: datetime
    category_id: int | None = None
    category: RelatedCategory | None = None
    thumbnail_id: int | None = None
    thumbnail: RelatedThumbnail | None = None


class BlogListResponse(PaginatedResponse):
    data: list[BlogRead] = []


class BlogCreate(BaseModel):
    slug: str
    title: str
    is_published: bool
    short_desc: str | None = None
    content: str | None = None
    meta_title: str | None = None
    meta_keywords: str | None = None
    meta_desc: str | None = None
    category_id: int | None = None
    thumbnail_id: int | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not SLUG_REGEX.match(v):
            raise ValueError(
                "Slug must be lowercase, alphanumeric, and may include hyphens"
            )
        return v


class BlogUpdate(BaseModel):
    slug: str
    title: str
    is_published: bool
    short_desc: str | None = None
    content: str | None = None
    meta_title: str | None = None
    meta_keywords: str | None = None
    meta_desc: str | None = None
    category_id: int | None = None
    thumbnail_id: int | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not SLUG_REGEX.match(v):
            raise ValueError(
                "Slug must be lowercase, alphanumeric, and may include hyphens"
            )
        return v


class BlogCategoryListQuery(PaginationQuery):
    search: str | None = None


class RelatedCategory(BaseModel):
    id: int
    name: str


class RelatedThumbnail(BaseModel):
    id: int
    url: str


class BlogCategoryReadList(BaseModel):
    id: int
    slug: str
    name: str
    thumbnail_id: int | None = None
    thumbnail: RelatedThumbnail | None = None


class BlogCategoryListResponse(PaginatedResponse):
    data: list[BlogCategoryReadList] = []


class BlogCategoryRead(BaseModel):
    id: int
    slug: str
    name: str
    short_desc: str | None = None
    meta_title: str | None = None
    meta_keywords: str | None = None
    meta_desc: str | None = None
    thumbnail_id: int | None = None
    thumbnail: RelatedThumbnail | None = None


class BlogCategoryCreate(BaseModel):
    slug: str
    name: str
    is_published: bool
    short_desc: str | None = None
    meta_title: str | None = None
    meta_keywords: str | None = None
    meta_desc: str | None = None
    thumbnail_id: int | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not SLUG_REGEX.match(v):
            raise ValueError(
                "Slug must be lowercase, alphanumeric, and may include hyphens"
            )
        return v


class BlogCategoryUpdate(BaseModel):
    slug: str
    name: str
    is_published: bool
    short_desc: str | None = None
    meta_title: str | None = None
    meta_keywords: str | None = None
    meta_desc: str | None = None
    thumbnail_id: int | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not SLUG_REGEX.match(v):
            raise ValueError(
                "Slug must be lowercase, alphanumeric, and may include hyphens"
            )
        return v
