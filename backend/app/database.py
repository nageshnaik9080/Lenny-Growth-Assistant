from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
from app.config import get_settings
from app.models.db_models import Base


def _normalize_db_url(url: str) -> str:
    """
    Render (and many cloud platforms) expose Postgres URLs as:
      postgres://...  or  postgresql://...
    SQLAlchemy's asyncpg driver requires:
      postgresql+asyncpg://...
    This function normalises any of the above forms.
    """
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    return url


settings = get_settings()
_db_url = _normalize_db_url(settings.database_url)
engine = create_async_engine(_db_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS transcript_chunks_embedding_hnsw
            ON transcript_chunks USING hnsw (embedding vector_cosine_ops)
        """))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
