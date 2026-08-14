import motor.motor_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from typing import AsyncGenerator
from fastapi import HTTPException

from .config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True
)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def test_connection() -> bool:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        return bool(result.scalar())

#MongoDB Setup

async def get_collection(collection_name: str):
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.ATLAS_DB_URI)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error {e}")

    database = client.skillissue
    collection = database.get_collection(collection_name)
    
    return collection
    