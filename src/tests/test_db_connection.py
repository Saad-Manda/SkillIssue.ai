from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio
from ..config import settings

async def test_connection():
    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.scalar())

asyncio.run(test_connection())