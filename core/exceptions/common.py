from typing import Literal
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError


class UnAuthorizedException(HTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(401, detail=msg or "UnAuthenticated")


class ForbiddenException(HTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(403, detail=msg or "Access Denied")


class NotFoundException(HTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(404, detail=msg or "Not Found")


class BadRequestErrorException(HTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(400, detail=msg or "Bad Request")


class FieldValidationError(RequestValidationError):
    def __init__(
        self, loc: Literal["body", "path", "query"], field_name: str, msg: str
    ) -> None:
        errors = [{"loc": [loc, field_name], "msg": msg}]
        super().__init__(errors=errors)
