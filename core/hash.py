from fastapi import Depends
from passlib.context import CryptContext
from typing import Annotated

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashUtills:
    def verify_hash(self, plane_string: str, hashed_string: str) -> bool:
        return pwd_context.verify(plane_string, hashed_string)

    def get_hash(self, password: str) -> str:
        return pwd_context.hash(password)


HashUtillsDependency = Annotated[HashUtills, Depends()]
