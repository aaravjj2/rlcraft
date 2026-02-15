pnpm install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e .
pnpm --filter web exec playwright install --with-deps chromium
make up
make wait-db
make migrate
