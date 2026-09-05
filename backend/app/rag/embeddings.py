"""
Embedding backend.

On Render's free tier (512 MB RAM), loading sentence-transformers + torch
exceeds the memory limit.  We therefore use OpenAI's text-embedding-3-small
API when OPENAI_API_KEY is set, and fall back to the local
sentence-transformers model only when running locally (where RAM is not a
constraint).
"""
import asyncio
import os
from functools import lru_cache

import httpx


# ── OpenAI embedding (cloud, ~1 KB RAM overhead) ───────────────────────────

_OPENAI_EMBED_URL = "https://api.openai.com/v1/embeddings"
_OPENAI_MODEL = "text-embedding-3-small"   # 1536-dim; free-tier friendly
_LOCAL_MODEL_DIM = 384                      # all-MiniLM-L6-v2 output dim


def _use_openai() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


async def _embed_openai(texts: list[str]) -> list[list[float]]:
    api_key = os.environ["OPENAI_API_KEY"]
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            _OPENAI_EMBED_URL,
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            json={"model": _OPENAI_MODEL, "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()
    # OpenAI returns embeddings in order
    return [item["embedding"] for item in sorted(data["data"],
                                                  key=lambda x: x["index"])]


# ── Local sentence-transformers (local dev only) ────────────────────────────

@lru_cache(maxsize=1)
def _get_local_model():
    from sentence_transformers import SentenceTransformer
    from app.config import get_settings
    return SentenceTransformer(get_settings().embedding_model)


async def _embed_local(texts: list[str]) -> list[list[float]]:
    model = _get_local_model()
    vectors = await asyncio.to_thread(
        model.encode, texts,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=False,
    )
    return vectors.tolist()


# ── Public API ──────────────────────────────────────────────────────────────

async def embed_text(text: str) -> list[float]:
    results = await embed_many([text])
    return results[0]


async def embed_many(texts: list[str]) -> list[list[float]]:
    if _use_openai():
        return await _embed_openai(texts)
    return await _embed_local(texts)
