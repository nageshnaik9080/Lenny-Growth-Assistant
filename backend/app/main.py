import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.database import init_db
from app.api import sessions, chat, health

logging.basicConfig(
    level=getattr(logging, get_settings().log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


async def auto_ingest_if_empty() -> None:
    """Run transcript ingestion on startup if the vector store is empty."""
    from pathlib import Path
    from sqlalchemy import text
    from app.database import SessionLocal

    transcript_dir = Path("/app/transcripts")
    files = [f for f in list(transcript_dir.glob("*.md")) + list(transcript_dir.glob("*.txt"))
             if f.name != ".gitkeep"]
    if not files:
        logger.info("No transcript files in /app/transcripts — skipping auto-ingest")
        return

    async with SessionLocal() as db:
        try:
            count = await db.scalar(text("SELECT COUNT(*) FROM transcript_chunks"))
        except Exception:
            count = 0

    if count and count > 0:
        logger.info("Transcript chunks already present (%d rows) — skipping auto-ingest", count)
        return

    logger.info("Vector store empty — auto-ingesting %d transcript files…", len(files))
    try:
        from scripts.ingest import ingest  # type: ignore
        await ingest()
        logger.info("Auto-ingest complete.")
    except Exception:
        logger.exception("Auto-ingest failed — app still starts but RAG will return no results")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Run ingestion as a background task so the server starts immediately
    # and health probes pass while ingestion proceeds in the background.
    asyncio.create_task(auto_ingest_if_empty())
    yield


app = FastAPI(title="Lenny Growth Assistant API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):
    logging.getLogger(__name__).exception("Unhandled request error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(health.router)


@app.get("/")
async def root():
    return {"name": "Lenny Growth Assistant API", "docs": "/docs"}
