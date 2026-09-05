import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/ingest", tags=["Ingest"])
logger = logging.getLogger(__name__)
_ingest_running = False


async def _run_ingest():
    global _ingest_running
    _ingest_running = True
    try:
        from scripts.ingest import ingest  # type: ignore
        await ingest()
        logger.info("Ingest completed successfully.")
    except Exception:
        logger.exception("Ingest failed.")
    finally:
        _ingest_running = False


@router.post("")
async def trigger_ingest(background_tasks: BackgroundTasks):
    """Trigger transcript ingestion as a background task."""
    if _ingest_running:
        return JSONResponse(status_code=409, content={"status": "already_running"})
    background_tasks.add_task(_run_ingest)
    return {"status": "started", "message": "Ingestion running in background. Check /api/health for vector_index status."}
