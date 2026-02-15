# Proof Manifest v1.2
Objective: Real Postgres+pgvector DEMO mode validation.
Scope: Dockerized Postgres 16 (pgvector) for migrations, ingest, API, tests, and E2E.
Commands: make up; make wait-db; make reset-db; make migrate; make ingest-fixtures; pnpm -r typecheck; pnpm -r test; pytest -q; pnpm --filter web build; pnpm --filter web e2e
Results: all commands completed successfully.
File inventory: logs/, playwright-report/, test-results/, screenshots/, TOUR.webm, manifest.json.
Known limitations: synthetic fixture data only; toy embedder used for deterministic demo matching.
