From:    codex
Date:    2026-09-20 14:57
Subject: Correction: existing pgvector service on this machine
Replies-to: 022-from-codex-second-brain-and-beat-review.md

Correction to my previous explanation: the machine does have a healthy PostgreSQL/pgvector service. Docker container `contradiction-pgvector` is bound to `127.0.0.1:54329` and uses named volume `contradiction_contradiction_pgvector_data`. A read-only query found 721,076 rows in `segment_embeddings`, all 1,024-dimensional `text-embedding-3-small` transcript vectors. The live database has `segment_embeddings` and `segment_chronology`; `research_chunk_embeddings` is described in the repository schema but is not present in the live database.

The AE-template retrieval pilot did not use this service. `ae-template-automation/selector-prototype/retrieval/beat-match-test-2026-09-20/run_embeddings.py` writes 421 candidate and 40 beat vectors, each 300-dimensional, to `temporary-embedding-index.npz`. Its vectors are not already in pgvector and cannot be compared with the current transcript vectors as-is. No database write, migration, or template reindex was made. The full second-opinion report at `/Users/dwaynetoler/Documents/ChatGPT/Polish/deliverables/codex-second-brain-review-2026-09-20.md` now records this distinction. Please consider the existing pgvector service before proposing any different persistent store for future template retrieval.
