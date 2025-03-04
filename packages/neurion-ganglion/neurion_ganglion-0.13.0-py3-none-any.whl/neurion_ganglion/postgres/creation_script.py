import asyncio

from neurion_ganglion.postgres import engine
from neurion_ganglion.postgres.ion_usage import Base


async def init_db():
    async with engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

asyncio.run(init_db())