from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import sessionmaker
from config.settings import get_config

config = get_config()
sync_engine = create_engine(
    url=config.get_sync_sqlite_dsn_url(),
    echo=False,
)
async_engine = create_async_engine(
    url=config.get_async_sqlite_dsn_url(),
    echo=False,
)

sync_sessionmaker = sessionmaker(sync_engine, expire_on_commit=False)
async_sessionmaker = async_sessionmaker(async_engine, expire_on_commit=False)
