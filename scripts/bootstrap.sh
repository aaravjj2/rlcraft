#!/usr/bin/env bash
set -euo pipefail
pnpm install
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
pnpm --filter web exec playwright install --with-deps chromium
make up
make wait-db
make migrate
