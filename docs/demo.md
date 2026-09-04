# 2–3 Minute Demo Script

## 0:00–0:20 — Start

Run:

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:3000`.

Say: "This is the Lenny Growth Assistant. It is grounded only in indexed Lenny transcript chunks."

## 0:20–0:55 — Grounded QA

Ask:

> What are the most important levers for improving activation?

Point to:

- provider badge = Ollama
- streamed answer
- source cards with episode/guest/topic

Explain that retrieval happens before generation and the model receives only the retrieved context.

## 0:55–1:15 — Refusal

Ask something unrelated, e.g.:

> What is the boiling point of water?

Show that the application can return the archive-insufficient response instead of pretending the podcast archive contains that fact.

## 1:15–1:50 — Ship 30 for 30

Switch mode to Ship 30 and ask:

> Turn the strongest activation insight into an actionable essay.

Show the right-side artifact:

- hook
- short paragraphs
- headers
- bold anchors
- checklist

## 1:50–2:15 — Security

Show HTML artifact mode and explain:

"HTML is sanitized and rendered in a sandboxed iframe. `allow-same-origin` is intentionally absent, so the artifact does not share the application's origin."

## 2:15–2:40 — Provider trade-off

Switch provider to Anthropic/OpenAI if configured.

Say:

"Local Ollama is the required evaluation path: lower marginal cost and no external API call, but weaker/smaller-model reasoning. Cloud routing provides stronger generation at the cost of API usage and network dependency."

## 2:40–3:00 — Architecture

Briefly show:

- PostgreSQL + pgvector HNSW
- FastAPI provider abstraction
- Next.js App Router
- Compose deployment
