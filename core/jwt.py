# core/jwt.py

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from fastapi import Depends
import jwt
from core import ConfigDepedency


class JwtUtils:
    def __init__(self, app_config: ConfigDepedency) -> None:
        self.app_config = app_config

    algotithm: str = "HS256"

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.app_config.access_token_expire_minutes
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.app_config.jwt_secrete, algorithm=self.algotithm
        )
        return encoded_jwt

    def get_payload(self, token: str) -> dict[str, Any] | None:
        try:
            payload = jwt.decode(
                token, self.app_config.jwt_secrete, algorithms=["HS256"]
            )
            return payload
        except jwt.InvalidTokenError:
            return None


JwtUtilsDepedency = Annotated[JwtUtils, Depends()]
