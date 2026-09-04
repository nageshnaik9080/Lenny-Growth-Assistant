import asyncio
import hashlib
import re
from datetime import datetime
from pathlib import Path

from sqlalchemy import select, text

from app.database import SessionLocal, init_db
from app.models.db_models import TranscriptChunk
from app.rag.embeddings import embed_many

TRANSCRIPT_DIR = Path("/app/transcripts")


def metadata_from_text(path: Path, text_value: str) -> tuple[str, str, str | None]:
    frontmatter = {}
    if text_value.startswith("---"):
        parts = text_value.split("---", 2)
        if len(parts) == 3:
            for line in parts[1].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    frontmatter[k.strip().lower()] = v.strip().strip('"')
    title = frontmatter.get("title") or path.stem.replace("_", " ").replace("-", " ").strip()
    guest = frontmatter.get("guest") or frontmatter.get("guest_name") or "Unknown"
    date = frontmatter.get("date") or frontmatter.get("publication_date")
    return title, guest, date


def timestamp_for(chunk: str) -> str | None:
    matches = re.findall(r'(?i)\b(?:\d{1,2}:)?\d{1,2}:\d{2}\b', chunk)
    return matches[0] if matches else None


def tokenize(s: str) -> list[str]:
    return re.findall(r"\S+", s)


def recursive_chunks(text_value: str, target_min=500, target_max=800, overlap=100) -> list[str]:
    """Recursive character-style splitting with a token-count target.

    Separators are tried from coarse to fine, while a token overlap is added
    between adjacent final chunks. This mirrors RecursiveCharacterTextSplitter
    behavior without introducing a heavyweight text-splitting dependency.
    """
    separators = ["\n\n", "\n", ". ", " ", ""]
    max_chars = target_max * 6
    min_chars = target_min * 4

    def split_rec(text: str, sep_index: int = 0) -> list[str]:
        if len(tokenize(text)) <= target_max:
            return [text.strip()] if text.strip() else []
        if sep_index >= len(separators):
            words = tokenize(text)
            return [" ".join(words[i:i + target_max]) for i in range(0, len(words), target_max)]

        sep = separators[sep_index]
        if sep == "":
            parts = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
        else:
            parts = text.split(sep)

        output = []
        current = ""
        for part in parts:
            candidate = f"{current}{sep}{part}" if current else part
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current.strip():
                    if len(tokenize(current)) >= target_min:
                        output.append(current.strip())
                    else:
                        output.extend(split_rec(current, sep_index + 1))
                current = part
        if current.strip():
            if len(tokenize(current)) >= target_min:
                output.append(current.strip())
            else:
                output.extend(split_rec(current, sep_index + 1))
        return output

    base = split_rec(text_value)
    result = []
    overlap_words = []
    for chunk in base:
        words = tokenize(chunk)
        if overlap_words:
            chunk = " ".join(overlap_words + words)
            words = tokenize(chunk)
        result.append(chunk.strip())
        overlap_words = words[-overlap:] if len(words) > overlap else words
    return result



async def ingest():
    await init_db()
    paths = sorted(list(TRANSCRIPT_DIR.glob("*.md")) + list(TRANSCRIPT_DIR.glob("*.txt")))
    if not paths:
        raise SystemExit(f"No .md/.txt transcript files found in {TRANSCRIPT_DIR}")

    async with SessionLocal() as db:
        total = 0
        for path in paths:
            raw = path.read_text(encoding="utf-8", errors="ignore")
            title, guest, pub_date = metadata_from_text(path, raw)
            chunks = recursive_chunks(raw)
            if not chunks:
                continue

            embeddings = await embed_many(chunks)
            for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                source_hash = hashlib.sha256(
                    f"{path.name}|{idx}|{chunk}".encode("utf-8")
                ).hexdigest()
                exists = await db.scalar(
                    select(TranscriptChunk.id).where(TranscriptChunk.source_hash == source_hash)
                )
                if exists:
                    continue
                db.add(
                    TranscriptChunk(
                        source_hash=source_hash,
                        episode_title=title,
                        guest_name=guest,
                        publication_date=pub_date,
                        timestamp_ref=timestamp_for(chunk),
                        chunk_index=idx,
                        chunk_text=chunk,
                        embedding=vector,
                    )
                )
                total += 1
            await db.commit()
            print(f"Ingested {path.name}: {len(chunks)} chunks")
        print(f"Inserted {total} new chunks.")


if __name__ == "__main__":
    asyncio.run(ingest())
