from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker;
from sqlmodel.ext.asyncio.session import AsyncSession;
from sqlmodel import SQLModel

import os
from dotenv import load_dotenv
load_dotenv()

DATABASE = os.getenv('DATABASE')
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_SCHEMA = os.getenv('DATABASE_SCHEMA')

DATABASE_URL = f"{DATABASE}+asyncpg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

SQLModel.metadata.schema = DATABASE_SCHEMA

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
       "server_settings": {
            "search_path": DATABASE_SCHEMA
        } 
    }
)

asyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with asyncSessionLocal() as session:
        yield session
