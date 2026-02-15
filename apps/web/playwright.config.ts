import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir:'./tests',
  workers:1,
  retries:0,
  reporter:[['html',{outputFolder:'playwright-report',open:'never'}]],
  use:{ baseURL:'http://127.0.0.1:4173', video:'on', trace:'on', screenshot:'on' },
  webServer:[
    { command:'DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rlc ../../.venv/bin/python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000', port:8000, reuseExistingServer:false },
    { command:'VITE_API_URL=http://127.0.0.1:8000 pnpm --filter web preview --host 0.0.0.0 --port 4173', port:4173, reuseExistingServer:false }
  ]
});
