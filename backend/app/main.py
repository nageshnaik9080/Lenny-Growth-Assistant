import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.database import init_db
from app.api import sessions, chat, health, ingest

logging.basicConfig(
    level=getattr(logging, get_settings().log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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
    return JSONResponse(status_code=500, content={"detail": str(exc)[:500]})


app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(health.router)
app.include_router(ingest.router)


@app.get("/")
async def root():
    return {"name": "Lenny Growth Assistant API", "docs": "/docs"}
