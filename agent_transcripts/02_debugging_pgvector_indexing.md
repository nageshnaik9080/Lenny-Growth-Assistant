# Agent Transcript 02 — Debugging pgvector Indexing

## Problem

Vector indexes depend on embedding dimension and distance metric being stable.

## Resolution

Use `sentence-transformers/all-MiniLM-L6-v2`, which produces 384-dimensional vectors, and create the HNSW index using cosine operations.

The ingestion code creates the `vector` extension before creating the vector column/index and performs an idempotent insert keyed by SHA-256 chunk hash.

## Operational note

If the embedding model is changed, the database vector dimension must be changed and the corpus re-ingested. Do not mix dimensions in one vector column.
