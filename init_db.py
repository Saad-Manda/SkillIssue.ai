"""
init_db.py — Database Initialization Script
============================================
Creates all PostgreSQL tables (defined in src/schemas/) if and only if
the target database is completely empty (no tables exist yet).

Usage:
    python init_db.py

Safe to re-run: exits without changes if tables already exist.
"""

import asyncio
import logging
import sys

from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from src.schemas.base import Base
from src.config import settings

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("init_db")


async def init_db() -> None:
    """Connect to PostgreSQL and create tables if the database is empty."""

    log.info("Connecting to database …")


    db_url: str = settings.DATABASE_URL
    if not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)

    # Detect if SSL is required before stripping the param
    ssl_required = query_params.pop("sslmode", [""])[0] == "require"
    query_params.pop("channel_binding", None)

    clean_url = urlunparse(parsed._replace(query=urlencode(query_params, doseq=True)))

    connect_args = {"ssl": True} if ssl_required else {}

    engine = create_async_engine(clean_url, echo=False, future=True, connect_args=connect_args)

    try:
        async with engine.connect() as conn:

            # ── Verify connectivity ───────────────────────────────────────
            await conn.execute(text("SELECT 1"))
            log.info("Connection successful.")

            # ── Check existing tables ─────────────────────────────────────
            existing_tables: list[str] = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )

            if existing_tables:
                log.info(
                    "Database already contains %d table(s): %s. "
                    "Skipping table creation.",
                    len(existing_tables),
                    ", ".join(sorted(existing_tables)),
                )
                return

            # ── Create all tables ─────────────────────────────────────────
            log.info("Database is empty. Creating tables …")
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()

            created_tables: list[str] = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )
            log.info(
                "✅  Successfully created %d table(s): %s",
                len(created_tables),
                ", ".join(sorted(created_tables)),
            )

    except Exception as exc:
        log.error("❌  Failed to initialize database: %s", exc)
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
