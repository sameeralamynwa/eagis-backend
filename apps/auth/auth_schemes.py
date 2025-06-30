from typing import Annotated
from fastapi import Cookie
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def cookie_token_scheme(auth_token: Annotated[str | None, Cookie()] = None):
    return auth_token
