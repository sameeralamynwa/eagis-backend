from sqlalchemy import select
from core.db import get_session
from .enums import Permissions, UserType
from core.hash import HashUtills
from .models import Role, User, Profile
from sqlalchemy.ext.asyncio import AsyncSession


async def seed_users():
    hash_utills = HashUtills()
    session_gen = get_session()
    session: AsyncSession = await anext(session_gen)

    role_moderator = await session.scalar(select(Role).where(Role.name == "moderator"))
    role_manager = await session.scalar(select(Role).where(Role.name == "manager"))

    if not role_moderator:
        role_moderator = Role(name="moderator", permissions=[Permissions.MANAGE_BLOGS])
        session.add(role_moderator)

    if not role_manager:
        role_manager = Role(
            name="manager",
            permissions=[Permissions.MANAGE_BLOGS, Permissions.MANAGE_USERS],
        )
        session.add(role_manager)

    admin_user = await session.scalar(select(User).where(User.username == "admin"))
    staff_user = await session.scalar(select(User).where(User.username == "staff"))
    user = await session.scalar(select(User).where(User.username == "user"))

    if not admin_user:
        admin_profile = Profile(avatar=None)

        admin_user = User(
            name="Admin",
            username="admin",
            email="admin@gmail.com",
            password=hash_utills.get_hash("123456789"),
            user_type=UserType.SUPER_ADMIN,
            email_verified=True,
            is_active=True,
            profile=admin_profile,
        )
        session.add(admin_user)
        session.add(admin_profile)

    if not staff_user:
        staff_profile = Profile(avatar=None)

        staff_user = User(
            name="Saff",
            username="staff",
            email="staff@gmail.com",
            password=hash_utills.get_hash("123456789"),
            user_type=UserType.Admin,
            email_verified=True,
            is_active=True,
            profile=staff_profile,
            roles=[role_moderator],
        )
        session.add(staff_user)
        session.add(staff_profile)

    if not user:
        profile = Profile(avatar=None)

        user = User(
            name="User",
            username="user",
            email="user@gmail.com",
            password=hash_utills.get_hash("123456789"),
            user_type=UserType.User,
            email_verified=True,
            is_active=True,
            profile=profile,
        )
        session.add(user)
        session.add(profile)

    await session.commit()
    print("Users Seeded")
