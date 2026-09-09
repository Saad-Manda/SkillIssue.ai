import asyncio
from logging.config import fileConfig
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from src.config import settings
from src.schemas.base import Base
import src.schemas  # noqa: F401 — registers all models on Base.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _async_db_url_and_connect_args() -> tuple[str, dict]:
    """Same asyncpg URL cleanup init_db.py uses (strip sslmode/channel_binding,
    force the +asyncpg driver, translate sslmode=require into connect_args)."""
    db_url = settings.DATABASE_URL
    if not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    ssl_required = query_params.pop("sslmode", [""])[0] == "require"
    query_params.pop("channel_binding", None)
    clean_url = urlunparse(parsed._replace(query=urlencode(query_params, doseq=True)))
    connect_args = {"ssl": True} if ssl_required else {}
    return clean_url, connect_args

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emits SQL, no DB connection)."""
    url, _ = _async_db_url_and_connect_args()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine."""
    url, connect_args = _async_db_url_and_connect_args()
    connectable = create_async_engine(url, poolclass=pool.NullPool, connect_args=connect_args)

    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
