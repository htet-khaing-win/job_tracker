from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os
from typing import AsyncGenerator

#Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:Nnaruto890@localhost/job_tracker")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

#Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo = True,
    poolclass = NullPool,
    future = True
)

#Create async session maker
AsyncSessionLocal = sessionmaker(
    engine,
    class_ =AsyncSession,
    expire_on_commit = False
)

#Dependecy for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

#Create tables
async def create_tables():
    from models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

#Drop all tables 
async def drop_tables():
    from models import Base
    async with engine.begin as conn:
        await conn.run_sync(Base.metadata.drop_all)