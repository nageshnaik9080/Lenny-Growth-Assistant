# Product Requirements Document — Lenny Growth Assistant

## 1. Product statement

The Lenny Growth Assistant is a retrieval-augmented assistant for Growth/Product PMs who want actionable product and growth tactics from Lenny's Podcast without manually searching hundreds of hours of conversations.

## 2. Persona

**Primary persona:** Growth/Product PM who needs a fast answer to an operational question and wants to know exactly which episode/guest supports the advice.

## 3. Problem

Podcast knowledge is high-value but difficult to operationalize: transcripts are long, fragmented and hard to search. Generic LLM answers create a trust problem because they can sound authoritative while being unsupported by the archive.

## 4. Goals

1. Answer only from retrieved transcript context.
2. Attribute claims with episode/guest/timestamp-or-topic citations.
3. Refuse when relevant context is insufficient.
4. Turn grounded insights into approximately 1,250-word Ship 30 for 30-style essays.
5. Show generated artifacts beside the chat.
6. Support local Ollama evaluation and cloud inference through the same provider interface.
7. Be deployable with Docker Compose.

## 5. Non-goals

- Reproducing or distributing the transcript archive.
- Training/fine-tuning an LLM.
- Treating general web knowledge as a source for grounded answers.
- Executing arbitrary user-generated code outside the sandboxed artifact iframe.

## 6. Success metrics

- Retrieval citation accuracy: **>= 90%**
- Local inference first-token latency: **< 4 seconds** under the target evaluation hardware/model after model warm-up
- Artifact render safety: **0 XSS vulnerabilities** in security test cases
- Grounded refusal rate: low-confidence/out-of-domain questions should not receive fabricated factual answers
- Service health: API health endpoint reports DB/vector/provider status

## 7. UX

Two-pane desktop experience:

- Left: session/chat/history/provider controls.
- Right: collapsible artifact preview.
- Mobile: artifact pane becomes an overlay/drawer.

## 8. Product trade-offs

### Local 3B/8B model
Pros: no per-token cloud cost, privacy, deterministic demo environment.
Cons: weaker reasoning/writing quality and potentially slower CPU inference.

### Cloud model
Pros: stronger reasoning and writing.
Cons: API cost, external data boundary, key management and network dependency.

### pgvector
Pros: PostgreSQL is already required for application state; one operational system.
Cons: vector workload competes with relational workload at larger scale; dedicated vector infrastructure may be preferable at very high volume.

### Strict retrieval threshold
Pros: reduces hallucination.
Cons: may reject borderline questions that a human could answer from several weak clues. Threshold is configurable.

## 9. Acceptance criteria

- `docker compose up --build` starts DB, backend, frontend and Ollama.
- `POST /api/sessions` creates a session.
- `POST /api/chat` streams grounded answer events.
- Chat responses include source metadata.
- `mode=ship30` generates a structured long-form artifact.
- Markdown and HTML artifacts render in the right pane.
- HTML uses DOMPurify and sandbox without `allow-same-origin`.
- Provider can be switched through API request.
- Tests cover retrieval, refusal, provider switching and API basics.
