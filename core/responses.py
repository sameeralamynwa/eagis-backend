from typing import Any
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    detail: str


class PaginatedResponse(BaseModel):
    data: Any | None = None
    per_page: int
    page: int
    total: int
