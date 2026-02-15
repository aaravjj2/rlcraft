import os
import subprocess
import pytest

DB='postgresql://postgres:postgres@localhost:5432/rlc'
os.environ['DATABASE_URL']=DB

@pytest.fixture(scope='session', autouse=True)
def _db_ready():
    subprocess.run(['make','up'], check=True)
    subprocess.run(['make','wait-db'], check=True)
    subprocess.run(['make','reset-db'], check=True)
    subprocess.run(['make','migrate'], check=True)
    env={**os.environ,'DATABASE_URL':DB}
    subprocess.run(['python','-m','ingest','ingest','--build-dir','fixtures/demo_build','--pack-name','demo','--pack-version','1.0','--mc-version','1.12.2'], check=True, env=env)
    bid=subprocess.check_output(['python','-m','ingest','latest-build-id'], env=env, text=True).strip()
    subprocess.run(['python','-m','ingest','ingest-images','--build-id',bid,'--images-dir','fixtures/images','--labels','fixtures/images/labels.json','--embedder','toy'], check=True, env=env)
    yield
