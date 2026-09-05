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
        # If the embedding column exists with wrong dimensions (384 from old
        # sentence-transformers ingestion), drop the table so it gets recreated
        # with the correct 1536 dimensions for OpenAI text-embedding-3-small.
        try:
            result = await conn.execute(text("""
                SELECT atttypmod FROM pg_attribute
                JOIN pg_class ON pg_class.oid = pg_attribute.attrelid
                WHERE pg_class.relname = 'transcript_chunks'
                AND pg_attribute.attname = 'embedding'
            """))
            row = result.fetchone()
            if row and row[0] == 384:
                await conn.execute(text("DROP TABLE IF EXISTS transcript_chunks CASCADE"))
                await conn.run_sync(Base.metadata.create_all)
        except Exception:
            pass
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS transcript_chunks_embedding_hnsw
            ON transcript_chunks USING hnsw (embedding vector_cosine_ops)
        """))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
