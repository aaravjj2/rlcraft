$ts=Get-Date -Format "yyyyMMdd-HHmmss"
$out="artifacts/proof/$ts-v1.2"
New-Item -ItemType Directory -Force -Path "$out/logs","$out/screenshots" | Out-Null
make up | Tee-Object "$out/logs/make-up.log"
make wait-db | Tee-Object "$out/logs/wait-db.log"
make reset-db | Tee-Object "$out/logs/reset-db.log"
make migrate | Tee-Object "$out/logs/migrate.log"
.\.venv\Scripts\Activate.ps1
make ingest-fixtures | Tee-Object "$out/logs/ingest.log"
pnpm -r typecheck | Tee-Object "$out/logs/typecheck.log"
pnpm -r test | Tee-Object "$out/logs/pnpm-test.log"
pytest -q | Tee-Object "$out/logs/pytest.log"
pnpm --filter web build | Tee-Object "$out/logs/web-build.log"
pnpm --filter web e2e | Tee-Object "$out/logs/e2e.log"
Copy-Item apps/web/playwright-report -Destination $out -Recurse
Copy-Item apps/web/test-results -Destination $out -Recurse
