import subprocess, os
from fastapi.testclient import TestClient
from apps.api.main import app

DB='postgresql://postgres:postgres@localhost:5432/rlc'
os.environ['DATABASE_URL']=DB
c=TestClient(app)

def build_id():
    return subprocess.check_output(['python','-m','ingest','latest-build-id'],text=True,env={**os.environ,'DATABASE_URL':DB}).strip()

def test_builds():
    r=c.get('/builds')
    assert r.status_code==200
    assert len(r.json())>=1

def test_items_and_recipes():
    bid=build_id()
    i=c.get('/items',params={'buildId':bid}).json()[0]['id']
    r=c.get(f'/items/{i}/recipes',params={'buildId':bid})
    assert r.status_code==200
    assert 'craftable' in r.json()

def test_image_search_golden_top_match():
    bid=build_id()
    with open('fixtures/images/tower_1.png','rb') as f:
        r=c.post('/structure-image-search',params={'buildId':bid},files={'file':('tower_1.png',f,'image/png')})
    assert r.status_code==200
    assert r.json()['matches'][0]['structure_key']=='demo:tower'
