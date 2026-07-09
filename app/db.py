from collections.abc import AsyncGenerator
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi import Depends

load_dotenv()

_raw_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Railway supplies postgresql:// but asyncpg requires postgresql+asyncpg://
if _raw_url.startswith("postgresql://"):
    DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgres://"):
    DATABASE_URL = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = _raw_url

_is_sqlite = DATABASE_URL.startswith("sqlite")


class Base(DeclarativeBase):
    pass


class User(Base, SQLAlchemyBaseUserTableUUID):
    posts = relationship("Post", back_populates="user")


if _is_sqlite:
    # SQLite doesn't have a native UUID type; store as string
    class Post(Base):
        __tablename__ = "posts"
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
        caption = Column(Text)
        url = Column(String, nullable=False)
        file_type = Column(String, nullable=False)
        file_name = Column(String, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        user = relationship("User", back_populates="posts")
else:
    from sqlalchemy.dialects.postgresql import UUID as PGUUID

    class Post(Base):  # type: ignore[no-redef]
        __tablename__ = "posts"
        id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(PGUUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
        caption = Column(Text)
        url = Column(String, nullable=False)
        file_type = Column(String, nullable=False)
        file_name = Column(String, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        user = relationship("User", back_populates="posts")


_engine_kwargs: dict = {}
if not _is_sqlite:
    _engine_kwargs = {"pool_size": 5, "max_overflow": 10, "pool_pre_ping": True}

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)
session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
