# Proof Manifest
Objective: validate demo build gates.
Commands: pnpm -r typecheck; pnpm -r test; pytest -q; pnpm --filter web build; pnpm --filter web e2e
Known limitations: Uses synthetic fixture data only.
