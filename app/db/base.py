from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import Settings

def create_engine_and_session(config: Settings):
    engine = create_async_engine(config.db_url,
                                 echo=False,
                                 future=True,
                                 pool_pre_ping=True,  # добавьте это
                                 pool_recycle=3600,
                                 )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False)
    return engine, session_factory


class Base(AsyncAttrs, DeclarativeBase):
    pass

