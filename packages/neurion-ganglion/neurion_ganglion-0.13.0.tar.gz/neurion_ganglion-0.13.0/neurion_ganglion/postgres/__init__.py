import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


def engine():
    return create_async_engine(os.getenv("POSTGRES_DATABASE_URL"), echo=True)

async def get_db():
    """Dependency to get database session."""
    AsyncSessionLocal = sessionmaker(bind=engine(), class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session


from typing import Callable, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")

async def with_db(func: Callable[[AsyncSession], T]) -> T:
    """
    A helper function to simplify database session management.

    Usage:
        result = await with_db(lambda postgres: IonUsageDAO.create_ion_usage(postgres))
    """
    async for db in get_db():
        return await func(db)