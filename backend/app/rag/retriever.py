from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.embeddings import embed_text


class TranscriptRetriever:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.35,
    ) -> list[dict]:
        query_vector = await embed_text(query)
        stmt = text("""
            SELECT episode_title, guest_name, chunk_text, timestamp_ref,
                   1 - (embedding <=> CAST(:vector AS vector)) AS similarity_score
            FROM transcript_chunks
            WHERE 1 - (embedding <=> CAST(:vector AS vector)) >= :threshold
            ORDER BY embedding <=> CAST(:vector AS vector)
            LIMIT :limit
        """)
        result = await self.session.execute(
            stmt,
            {"vector": str(query_vector), "threshold": similarity_threshold, "limit": top_k},
        )
        return [
            {
                "episode": row.episode_title,
                "guest": row.guest_name,
                "text": row.chunk_text,
                "timestamp": row.timestamp_ref,
                "score": float(row.similarity_score),
            }
            for row in result.fetchall()
        ]
