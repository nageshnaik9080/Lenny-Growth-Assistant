from unittest.mock import AsyncMock
import pytest
from app.rag.retriever import TranscriptRetriever


@pytest.mark.asyncio
async def test_retrieval_orders_and_maps_rows(monkeypatch):
    import app.rag.retriever as module
    monkeypatch.setattr(module, "embed_text", AsyncMock(return_value=[0.1, 0.2]))
    session = AsyncMock()
    row = type("Row", (), {
        "episode_title": "Growth Episode",
        "guest_name": "Guest",
        "chunk_text": "Activation insight",
        "timestamp_ref": "12:34",
        "similarity_score": 0.82,
    })()
    result = type("Result", (), {"fetchall": lambda self: [row]})()
    session.execute.return_value = result

    items = await TranscriptRetriever(session).retrieve_relevant_chunks("activation", 5, 0.35)
    assert items[0]["score"] == 0.82
    assert items[0]["episode"] == "Growth Episode"
