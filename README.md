# Custom RLCraft Wiki / Knowledge Base (Demo Mode, Real Postgres+pgvector v1.2)
SYNTHETIC DEMO DATA ONLY. Do not copy external wiki text/images without permission.

## Quickstart
1. Run `scripts/bootstrap.sh`
2. `make reset-db && make migrate && make ingest-fixtures`
3. Run API: `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rlc uvicorn apps.api.main:app --reload`
4. Run web: `VITE_API_URL=http://127.0.0.1:8000 pnpm --filter web dev`
5. Run proof: `./scripts/proof.sh`
