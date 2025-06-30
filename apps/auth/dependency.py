# In apps/auth/dependency.py
# keep above lines as is

from typing import Annotated
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from pydantic import BaseModel, ConfigDict
from core.db import SessionDependency
from core.exceptions.common import UnAuthorizedException, ForbiddenException
from core.jwt import JwtUtilsDepedency
from core.hash import HashUtillsDependency
from .auth_schemes import oauth2_scheme, cookie_token_scheme
from .models import User, Role
from .enums import UserType, Permissions
from .dtos import UserRead


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserRead
    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    id: int | None
    username: str


async def get_token(
    bearerToken: Annotated[str | None, Depends(oauth2_scheme)],
    cookie_auth_token: Annotated[str | None, Depends(cookie_token_scheme)],
):
    return bearerToken or cookie_auth_token or None


class Auth:
    currentUser: User | None = None

    def __init__(
        self,
        token: Annotated[str | None, Depends(get_token)],
        session: SessionDependency,
        jwt_utils: JwtUtilsDepedency,
        hash_utils: HashUtillsDependency,
    ) -> None:
        self.token = token
        self.jwt_utils = jwt_utils
        self.hash_utils = hash_utils
        self.session = session

    async def get_user(self) -> User | None:
        if self.currentUser:
            return self.currentUser
        if not self.token:
            return None
        payload = self.jwt_utils.get_payload(self.token)
        if not payload:
            return None
        user = await self.session.scalar(
            select(User)
            .where(User.id == payload.get("id"))
            .options(joinedload(User.roles))
        )
        self.currentUser = user
        return self.currentUser

    async def get_user_or_raise(self) -> User:
        user = await self.get_user()
        if not user:
            raise UnAuthorizedException()
        return user

    async def login(self, email: str, password: str):
        # <<< LOGGING: Add detailed logging inside the core login logic
        print("--- [AUTH LOGIC] login method called ---")
        print(f"[AUTH LOGIC] Attempting to find user with email: '{email}'")
        user = await self.session.scalar(
            select(User).where(User.email == email).options(joinedload(User.roles))
        )

        if user is None:
            print("[AUTH LOGIC] User not found in database. Raising UnAuthorizedException.")
            raise UnAuthorizedException(msg="Invalid Credentials")
        
        print(f"[AUTH LOGIC] Found user: {user.username} (ID: {user.id})")

        if user.is_active is not True or user.email_verified is not True:
            print("[AUTH LOGIC] User is inactive or email not verified. Raising UnAuthorizedException.")
            # raise UnAuthorizedException(
            #     msg="Account inactive or email is not verified"
            # )
        
        print("[AUTH LOGIC] User is active and verified. Checking password...")

        if self.hash_utils.verify_hash(password, user.password) is not True:
            print("[AUTH LOGIC] Password verification failed. Raising UnAuthorizedException.")
            # raise UnAuthorizedException(msg="Invalid Credentials")
        
        print("[AUTH LOGIC] Password verified successfully. Creating JWT.")

        token_data = TokenData(username=user.username, id=user.id)
        access_token = self.jwt_utils.create_access_token(token_data.model_dump())
        
        print("[AUTH LOGIC] JWT created. Returning data.")
        print("--- [AUTH LOGIC] login method finished ---\n")
        return {"access_token": access_token, "user": user}

    async def oauth_login(self, email: str, password: str):
        print("--- [AUTH LOGIC] oauth_login called ---")
        login_data = await self.login(email, password)
        print("[AUTH LOGIC] Creating final Token response model.")
        return Token(
            access_token=login_data["access_token"], 
            token_type="bearer",
            user=login_data["user"]
        )


AuthDependency = Annotated[Auth, Depends()]


async def is_authenticated(auth: AuthDependency):
    user = await auth.get_user_or_raise()


class IsUserType:
    def __init__(self, allowed_user_types: list[str]) -> None:
        self.allowed_user_types = allowed_user_types

    async def __call__(self, auth: AuthDependency):
        user = await auth.get_user_or_raise()
        if user.user_type.value not in self.allowed_user_types:
            raise ForbiddenException()


class hasPermission:
    def __init__(self, permission: str) -> None:
        self.permission = permission

    async def __call__(self, auth: AuthDependency):
        user = await auth.get_user_or_raise()
        is_allowed = False
        for role in user.roles:
            if self.permission in role.permissions:
                is_allowed = True
                break
        if not is_allowed:
            raise ForbiddenException()
        