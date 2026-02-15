# Proof Manifest v1.1
Objective: DB-Wired Demo Mode validation.
Scope: Postgres+pgvector wired API/ingest/frontend gates.
Commands: make up; make reset-db; make migrate; make ingest-fixtures; pnpm -r typecheck; pnpm -r test; pytest -q; pnpm --filter web build; pnpm --filter web e2e
Results: all commands completed successfully.
File inventory: logs/, playwright-report/, test-results/, screenshots/, TOUR.webm, manifest.json.
Known limitations: demo synthetic fixtures only; toy embedder default.
