import json, hashlib, subprocess, os
import psycopg

DB='postgresql://postgres:postgres@localhost:5432/rlc'

def table_digest(conn):
    data={}
    with conn.cursor() as cur:
        tables=['entity_item','entity_mob','recipe','recipe_input','recipe_output','item_used_in','mob_spawn_rule','structure','structure_image']
        for t in tables:
            cur.execute(f"select row_to_json(x) from (select * from {t} order by 1,2) x")
            data[t]=[r[0] for r in cur.fetchall()]
        cur.execute("select structure_image_id::text, embedding::text from structure_embedding order by 1")
        data['structure_embedding']=cur.fetchall()
    s=json.dumps(data,sort_keys=True,default=str)
    return hashlib.sha256(s.encode()).hexdigest()

def reingest_fresh():
    subprocess.run(['make','reset-db'],check=True)
    subprocess.run(['make','migrate'],check=True)
    env={**os.environ,'DATABASE_URL':DB}
    subprocess.run(['python','-m','ingest','ingest','--build-dir','fixtures/demo_build','--pack-name','demo','--pack-version','1.0','--mc-version','1.12.2'],check=True,env=env)
    bid=subprocess.check_output(['python','-m','ingest','latest-build-id'],text=True,env=env).strip()
    subprocess.run(['python','-m','ingest','ingest-images','--build-id',bid,'--images-dir','fixtures/images','--labels','fixtures/images/labels.json','--embedder','toy'],check=True,env=env)

def test_determinism_ingest_db_hash():
    reingest_fresh()
    with psycopg.connect(DB) as c1: h1=table_digest(c1)
    reingest_fresh()
    with psycopg.connect(DB) as c2: h2=table_digest(c2)
    assert h1==h2
