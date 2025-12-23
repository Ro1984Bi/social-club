import uuid
from datetime import datetime, UTC   
from collections.abc import AsyncGenerator
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi import Depends

DATABASE_URL = 'sqlite+aiosqlite:///./test.db'

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
  # We explicitly define the name to match the Post ForeignKey
    __tablename__ = "users" 
    
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = 'posts'

# Note: For SQLite, UUIDs can be challenging. We use the SQLAlchemy UUID type

# which is compatible with PostgreSQL and adaptable to others.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # This must match the __tablename__ of User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    # Important: We removed the parentheses from datetime.now(UTC)

# so that it executes when the record is created, not when the server starts.
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="posts")


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)