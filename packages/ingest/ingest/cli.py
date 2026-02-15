import argparse, hashlib, json, os, uuid
from pathlib import Path
import psycopg

from .embed import ToyEmbedder


def stable_hash_obj(obj)->str:
    s=json.dumps(obj,sort_keys=True,separators=(',',':'))
    return hashlib.sha256(s.encode()).hexdigest()


def get_conn():
    url=os.getenv('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL is required')
    return psycopg.connect(url)


def checksums(build_dir:Path):
    modlist=(build_dir/'modlist.txt').read_text() if (build_dir/'modlist.txt').exists() else 'demo-modlist'
    files=[]
    for sub in ['config','scripts']:
        d=build_dir/sub
        if d.exists():
            for f in sorted(d.rglob('*')):
                if f.is_file():
                    files.append((str(f.relative_to(build_dir)),f.read_text(errors='ignore')))
    return hashlib.sha256(modlist.encode()).hexdigest(), hashlib.sha256(stable_hash_obj(files).encode()).hexdigest()


def ingest(build_dir:str, pack_name:str, pack_version:str, mc_version:str):
    p=Path(build_dir)
    mod_checksum,cfg_checksum=checksums(p)
    build_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f'{pack_name}:{pack_version}:{mc_version}:{mod_checksum}:{cfg_checksum}'))

    items=json.loads((p/'exports/items.json').read_text())
    mobs=json.loads((p/'exports/mobs.json').read_text())
    recipes=json.loads((p/'exports/recipes.json').read_text())
    spawns=json.loads((p/'config/spawners/lycanites_like.json').read_text())['rules']
    structures=[
        {'structure_key':'demo:tower','name':'Sky Tower','type':'synthetic'},
        {'structure_key':'demo:dungeon','name':'Deep Dungeon','type':'synthetic'},
        {'structure_key':'demo:village','name':'Safe Village','type':'synthetic'}
    ]

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "insert into pack_build(build_id,pack_name,pack_version,mc_version,modlist_checksum,config_checksum) values (%s::uuid,%s,%s,%s,%s,%s) on conflict do nothing",
            (build_id,pack_name,pack_version,mc_version,mod_checksum,cfg_checksum)
        )

        for i in sorted(items,key=lambda x:x['item_key']):
            cur.execute(
                "insert into entity_item(id,build_id,item_key,name,mod,raw_json) values (%s::uuid,%s::uuid,%s,%s,%s,%s::jsonb)",
                (str(uuid.uuid5(uuid.NAMESPACE_URL,build_id+':item:'+i['item_key'])),build_id,i['item_key'],i['name'],i.get('mod','demo'),json.dumps(i,sort_keys=True))
            )

        for m in sorted(mobs,key=lambda x:x['mob_key']):
            cur.execute(
                "insert into entity_mob(id,build_id,mob_key,name,mod,raw_json) values (%s::uuid,%s::uuid,%s,%s,%s,%s::jsonb)",
                (str(uuid.uuid5(uuid.NAMESPACE_URL,build_id+':mob:'+m['mob_key'])),build_id,m['mob_key'],m['name'],m.get('mod','demo'),json.dumps(m,sort_keys=True))
            )

        for s in structures:
            cur.execute(
                "insert into structure(id,build_id,structure_key,name,type,raw_json) values (%s::uuid,%s::uuid,%s,%s,%s,%s::jsonb)",
                (str(uuid.uuid5(uuid.NAMESPACE_URL,build_id+':struct:'+s['structure_key'])),build_id,s['structure_key'],s['name'],s['type'],json.dumps(s,sort_keys=True))
            )

        for r in sorted(recipes,key=lambda x:x['recipe_key']):
            rid=str(uuid.uuid5(uuid.NAMESPACE_URL,build_id+':recipe:'+r['recipe_key']))
            cur.execute(
                "insert into recipe(id,build_id,recipe_key,type,raw_json) values (%s::uuid,%s::uuid,%s,%s,%s::jsonb)",
                (rid,build_id,r['recipe_key'],r.get('type','crafting'),json.dumps(r,sort_keys=True))
            )
            for idx,inp in enumerate(r.get('inputs',[])):
                cur.execute(
                    "insert into recipe_input(id,recipe_id,item_key,qty,meta) values (%s::uuid,%s::uuid,%s,%s,%s::jsonb)",
                    (str(uuid.uuid5(uuid.NAMESPACE_URL,rid+':in:'+str(idx))),rid,inp['item_key'],inp.get('qty',1),json.dumps(inp,sort_keys=True))
                )
                cur.execute(
                    "insert into item_used_in(id,build_id,item_key,recipe_id) values (%s::uuid,%s::uuid,%s,%s::uuid)",
                    (str(uuid.uuid5(uuid.NAMESPACE_URL,rid+':used:'+str(idx))),build_id,inp['item_key'],rid)
                )
            for idx,out in enumerate(r.get('outputs',[])):
                cur.execute(
                    "insert into recipe_output(id,recipe_id,item_key,qty,meta) values (%s::uuid,%s::uuid,%s,%s,%s::jsonb)",
                    (str(uuid.uuid5(uuid.NAMESPACE_URL,rid+':out:'+str(idx))),rid,out['item_key'],out.get('qty',1),json.dumps(out,sort_keys=True))
                )

        for idx,s in enumerate(sorted(spawns,key=lambda x:(x['mob_key'],x.get('dimension',''),x.get('biome','')))):
            cur.execute(
                "insert into mob_spawn_rule(id,build_id,mob_key,dimension,biome,conditions) values (%s::uuid,%s::uuid,%s,%s,%s,%s::jsonb)",
                (str(uuid.uuid5(uuid.NAMESPACE_URL,build_id+':spawn:'+str(idx))),build_id,s['mob_key'],s.get('dimension',''),s.get('biome',''),json.dumps(s.get('conditions',{}),sort_keys=True))
            )

        conn.commit()

    outdir=Path('artifacts/derived')/build_id
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/'build_report.json').write_text(json.dumps({'build_id':build_id},sort_keys=True,indent=2))
    return {'build_id':build_id}


def latest_build_id():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('select build_id::text from pack_build order by created_at desc limit 1')
        r=cur.fetchone()
    return r[0] if r else ''


def ingest_images(build_id:str, images_dir:str, labels:str):
    emb=ToyEmbedder()
    labels_map=json.loads(Path(labels).read_text())
    rows=[]

    with get_conn() as conn, conn.cursor() as cur:
        for img in sorted(labels_map):
            key=labels_map[img]
            data=(Path(images_dir)/img).read_bytes()
            v=emb.embed_bytes(data)
            iid=str(uuid.uuid5(uuid.NAMESPACE_URL,build_id+':img:'+img))
            cur.execute(
                "insert into structure_image(id,build_id,structure_key,image_url,label_source,meta) values (%s::uuid,%s::uuid,%s,%s,%s,%s::jsonb) on conflict do nothing",
                (iid,build_id,key,img,'fixture',json.dumps({'label':'synthetic'},sort_keys=True))
            )
            cur.execute(
                "insert into structure_embedding(structure_image_id,embedding,meta) values (%s::uuid,%s::vector,%s::jsonb) on conflict (structure_image_id) do update set embedding=excluded.embedding, meta=excluded.meta",
                (iid,'['+','.join(f'{x:.8f}' for x in v)+']',json.dumps({},sort_keys=True))
            )
            rows.append({'image':img,'structure_key':key,'embedding':v})
        conn.commit()

    out=Path('artifacts/derived')/build_id
    out.mkdir(parents=True,exist_ok=True)
    (out/'image_embeddings.json').write_text(json.dumps(rows,indent=2,sort_keys=True))
    return rows


def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    i=sub.add_parser('ingest'); i.add_argument('--build-dir',required=True); i.add_argument('--pack-name',required=True); i.add_argument('--pack-version',required=True); i.add_argument('--mc-version',required=True)
    ii=sub.add_parser('ingest-images'); ii.add_argument('--build-id',required=True); ii.add_argument('--images-dir',required=True); ii.add_argument('--labels',required=True); ii.add_argument('--embedder',default='toy')
    sub.add_parser('latest-build-id')
    a=ap.parse_args()
    if a.cmd=='ingest': print(json.dumps(ingest(a.build_dir,a.pack_name,a.pack_version,a.mc_version)))
    elif a.cmd=='ingest-images': print(json.dumps(ingest_images(a.build_id,a.images_dir,a.labels)))
    else: print(latest_build_id())

if __name__=='__main__':
    main()
