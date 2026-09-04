# Agent Transcript 01 — Initial Scaffolding

## Objective

Translate the assignment into independently testable layers:

1. Documentation
2. Persistence
3. Embedding/retrieval
4. Provider abstraction
5. API/SSE
6. Frontend
7. Artifact security
8. Containerization
9. Tests

## Key decision

Keep retrieval and provider routing independent. This makes Ollama/cloud switching a runtime concern rather than a rewrite of the RAG agent.

## Expected result

A fresh checkout can start with Docker Compose even before transcripts are ingested; the assistant should refuse unsupported factual questions instead of hallucinating.
