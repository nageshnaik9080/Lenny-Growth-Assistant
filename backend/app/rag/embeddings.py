from functools import lru_cache
import asyncio
from sentence_transformers import SentenceTransformer
from app.config import get_settings


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model)


async def embed_text(text: str) -> list[float]:
    model = get_model()
    vector = await asyncio.to_thread(model.encode, text, normalize_embeddings=True)
    return vector.tolist()


async def embed_many(texts: list[str]) -> list[list[float]]:
    model = get_model()
    vectors = await asyncio.to_thread(model.encode, texts, normalize_embeddings=True, batch_size=32, show_progress_bar=True)
    return vectors.tolist()
