from pydantic import BaseModel


class PaginationQuery(BaseModel):
    page: int = 1
    per_page: int = 20
