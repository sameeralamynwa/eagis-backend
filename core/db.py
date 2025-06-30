from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from core import get_config
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from .base_model import BaseModel

config = get_config()

async_engine = create_async_engine(config.db_connection, echo=True, future=True)


async def create_db_and_tables():
    async with async_engine.connect() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async_session_factory = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    session = async_session_factory()
    async with session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]
