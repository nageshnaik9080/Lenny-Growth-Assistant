# Lenny Growth Assistant

A production-oriented full-stack RAG application for grounded product/growth answers over Lenny's Podcast transcripts, with a Ship 30 for 30 essay engine and a secure Claude-Artifacts-style viewer.

## What is included

- FastAPI + async SQLAlchemy + PostgreSQL/pgvector
- HNSW cosine-similarity index
- Recursive transcript chunking at roughly 500–800 tokens with ~100-token overlap
- Sentence Transformers `all-MiniLM-L6-v2` embeddings (384 dimensions)
- Dynamic Ollama/local vs Anthropic/OpenAI cloud routing
- SSE token streaming
- Grounded source citations and low-relevance refusal
- Ship 30 for 30 ~1,250-word writing mode
- Markdown artifact rendering with GFM
- HTML/CSS artifact rendering in `<iframe sandbox="allow-scripts">` without `allow-same-origin`
- DOMPurify sanitization
- PostgreSQL persistence for sessions, messages, and artifacts
- Docker Compose for DB, backend, frontend, Ollama and model initialization
- Pytest unit/integration tests
- PRD, architecture and design specifications
- Demo script and deployment handoff

## 1. Prerequisites

For the local Ollama evaluation, the reference assignment recommends at least 4 CPU cores, 16 GB RAM and ~15 GB free disk. Docker 24+ and Compose are recommended.

## 2. Start the stack

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

The first run downloads the Ollama model and the embedding model, so startup/first query can be slow.

## 3. Ingest transcripts

The assignment requires obtaining the public Lenny transcript archive. The downloader is intentionally configurable rather than hard-coding a brittle third-party URL.

Option A — clone/download the transcript repository into `transcripts/` yourself:

```bash
mkdir -p transcripts
# Copy .md/.txt episode files into ./transcripts
```

Option B — configure `TRANSCRIPT_SOURCE_URL` in your shell and run:

```bash
docker compose run --rm backend python scripts/download_transcripts.py
```

For a Git repository URL, the downloader can clone it when `GIT_REPOSITORY=1`.

Then ingest:

```bash
docker compose run --rm backend python scripts/ingest.py
```

The ingestion script is idempotent by chunk hash.

## 4. Environment variables

See `.env.example`.

Important:

- `DEFAULT_LLM_PROVIDER=ollama` satisfies the local demo requirement.
- `OLLAMA_BASE_URL=http://ollama:11434` is correct inside Compose.
- Set `DEFAULT_LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` for Claude.
- Or set `DEFAULT_LLM_PROVIDER=openai` and `OPENAI_API_KEY`.
- The frontend can override provider per request without code changes.
- `RETRIEVAL_THRESHOLD` is configurable because cosine-score distributions vary with corpus/domain.

## 5. API examples

Create a session:

```bash
curl -X POST http://localhost:8000/api/sessions \
  -H 'content-type: application/json' \
  -d '{"title":"Growth ideas"}'
```

Chat:

```bash
curl -N -X POST http://localhost:8000/api/chat \
  -H 'content-type: application/json' \
  -d '{
    "session_id":"<UUID>",
    "message":"How should a PM improve activation?",
    "mode":"default",
    "provider":"ollama"
  }'
```

Generate a Ship 30 for 30 artifact:

```json
{
  "session_id": "<UUID>",
  "message": "Turn the strongest activation insight into a practical essay.",
  "mode": "ship30",
  "provider": "ollama"
}
```

## 6. Local development without Docker

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

You still need PostgreSQL/pgvector and Ollama running locally.

## 7. Tests

Fast unit tests:

```bash
cd backend
pytest -q
```

The database integration tests are skipped unless `TEST_DATABASE_URL` is provided and reachable.

## 8. Security model

HTML artifacts are treated as untrusted. The browser applies DOMPurify before assigning `srcDoc`, and the iframe uses `sandbox="allow-scripts"` with no `allow-same-origin`. This deliberately prevents the artifact from sharing the parent origin/cookies/localStorage.

The sanitizer does not permit frames, forms, object/embed, meta refresh, or base tags. Scripts are retained only because the assignment explicitly requires interactive HTML artifacts; the sandbox is the primary isolation boundary.

## 9. Demo

Use `docs/demo.md` for the required 2–3 minute walkthrough. The demo should show:

1. Local Ollama provider.
2. A grounded transcript question with citations.
3. Low-context/out-of-domain refusal.
4. Ship 30 for 30 mode and artifact preview.
5. Provider switch to cloud, if an API key is available.
6. Architecture trade-off: local cost/privacy vs cloud quality.

## 10. Important limitation

This repository includes the ingestion pipeline but does not redistribute Lenny's copyrighted transcript archive. To have meaningful grounded answers, place the permitted transcript files in `./transcripts` and run ingestion.

The application is runnable immediately with `docker compose up --build`; without transcripts, the UI/API will correctly report that the archive has insufficient information rather than fabricate answers.
