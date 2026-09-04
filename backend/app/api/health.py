from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import get_db
from app.providers.ollama_provider import OllamaProvider

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
async def health(db: AsyncSession = Depends(get_db)):
    status = {"db": False, "vector_index": False, "ollama": False}
    try:
        await db.execute(text("SELECT 1"))
        status["db"] = True
        count = await db.execute(text("SELECT COUNT(*) FROM transcript_chunks"))
        status["vector_index"] = count.scalar_one() > 0
    except Exception:
        pass
    status["ollama"] = await OllamaProvider().health()
    return {"status": "ok" if status["db"] else "degraded", **status}
