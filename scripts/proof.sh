#!/usr/bin/env bash
set -euo pipefail
TS=$(date +%Y%m%d-%H%M%S)
OUT="artifacts/proof/${TS}-v1.2"
mkdir -p "$OUT/logs" "$OUT/screenshots"
make up | tee "$OUT/logs/make-up.log"
make wait-db | tee "$OUT/logs/wait-db.log"
make reset-db | tee "$OUT/logs/reset-db.log"
make migrate | tee "$OUT/logs/migrate.log"
source .venv/bin/activate
make ingest-fixtures | tee "$OUT/logs/ingest.log"
pnpm -r typecheck | tee "$OUT/logs/typecheck.log"
pnpm -r test | tee "$OUT/logs/pnpm-test.log"
pytest -q | tee "$OUT/logs/pytest.log"
pnpm --filter web build | tee "$OUT/logs/web-build.log"
pnpm --filter web e2e | tee "$OUT/logs/e2e.log"
cp -r apps/web/playwright-report "$OUT/"
cp -r apps/web/test-results "$OUT/"
find apps/web/test-results -name '*.webm' | head -n1 | xargs -I{} cp {} "$OUT/TOUR.webm"
cp apps/web/test-results/e2e-tour-flow/test-finished-1.png "$OUT/screenshots/checkpoint-tour.png"
cat > "$OUT/MANIFEST.md" <<M
# Proof Manifest v1.2
Objective: Real Postgres+pgvector DEMO mode validation.
Scope: Dockerized Postgres 16 (pgvector) for migrations, ingest, API, tests, and E2E.
Commands: make up; make wait-db; make reset-db; make migrate; make ingest-fixtures; pnpm -r typecheck; pnpm -r test; pytest -q; pnpm --filter web build; pnpm --filter web e2e
Results: all commands completed successfully.
File inventory: logs/, playwright-report/, test-results/, screenshots/, TOUR.webm, manifest.json.
Known limitations: synthetic fixture data only; toy embedder used for deterministic demo matching.
M
cat > "$OUT/README.md" <<M
Re-run: ./scripts/proof.sh then inspect logs and reports in this folder.
M
cat > "$OUT/manifest.json" <<M
{"milestone":"v1.2","timestamp":"$TS","database":"postgres16+pgvector"}
M
echo "$OUT"
