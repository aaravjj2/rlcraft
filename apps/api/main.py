from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .repo import fetch_all, fetch_one
from packages.ingest.ingest.embed import ToyEmbedder

app = FastAPI(title='RLCraft KB API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.get('/builds')
def get_builds():
    return fetch_all("select build_id::text as build_id, pack_name, pack_version, mc_version from pack_build order by created_at desc")

@app.get('/mobs')
def get_mobs(buildId:str,q:str='',dimension:str='',biome:str='',page:int=1):
    return fetch_all("select mob_key as id, name, mod from entity_mob where build_id=%s::uuid and lower(name) like lower(%s) order by name", (buildId, f'%{q}%'))

@app.get('/mobs/{mobId}')
def get_mob(mobId:str, buildId:str):
    try:
        return fetch_one("select mob_key as id, name, mod, raw_json from entity_mob where build_id=%s::uuid and mob_key=%s", (buildId,mobId))
    except KeyError:
        raise HTTPException(404)

@app.get('/mobs/{mobId}/spawns')
def get_spawns(mobId:str, buildId:str):
    return fetch_all("select dimension, biome, conditions from mob_spawn_rule where build_id=%s::uuid and mob_key=%s order by dimension, biome", (buildId,mobId))

@app.get('/items')
def get_items(buildId:str,q:str='',mod:str='',page:int=1):
    return fetch_all("select item_key as id, name, mod from entity_item where build_id=%s::uuid and lower(name) like lower(%s) and (%s='' or mod=%s) order by name", (buildId,f'%{q}%',mod,mod))

@app.get('/items/{itemId}')
def get_item(itemId:str, buildId:str):
    try:
        return fetch_one("select item_key as id, name, mod, raw_json from entity_item where build_id=%s::uuid and item_key=%s", (buildId,itemId))
    except KeyError:
        raise HTTPException(404)

@app.get('/items/{itemId}/recipes')
def get_item_recipes(itemId:str, buildId:str):
    craft=fetch_all("select r.recipe_key, r.type from recipe r join recipe_output o on o.recipe_id=r.id where r.build_id=%s::uuid and o.item_key=%s order by r.recipe_key", (buildId,itemId))
    used=fetch_all("select r.recipe_key, r.type from recipe r join recipe_input i on i.recipe_id=r.id where r.build_id=%s::uuid and i.item_key=%s order by r.recipe_key", (buildId,itemId))
    return {'craftable':craft,'used_in':used}

@app.get('/structures')
def get_structures(buildId:str,q:str='',dimension:str='',biome:str='',page:int=1):
    return fetch_all("select structure_key as id, name, type from structure where build_id=%s::uuid and lower(name) like lower(%s) order by name", (buildId,f'%{q}%'))

@app.get('/structures/{structureId}')
def get_structure(structureId:str, buildId:str):
    s=fetch_one("select structure_key as id, name, type, raw_json from structure where build_id=%s::uuid and structure_key=%s", (buildId,structureId))
    s['images']=fetch_all("select image_url from structure_image where build_id=%s::uuid and structure_key=%s order by image_url",(buildId,structureId))
    return s

@app.get('/search')
def search(buildId:str,q:str):
    return {
        'items': fetch_all("select item_key as id, name from entity_item where build_id=%s::uuid and lower(name) like lower(%s) order by name",(buildId,f'%{q}%')),
        'mobs': fetch_all("select mob_key as id, name from entity_mob where build_id=%s::uuid and lower(name) like lower(%s) order by name",(buildId,f'%{q}%')),
        'structures': fetch_all("select structure_key as id, name from structure where build_id=%s::uuid and lower(name) like lower(%s) order by name",(buildId,f'%{q}%')),
    }

@app.post('/structure-image-search')
async def structure_image_search(buildId:str, file:UploadFile, k:int=3):
    q=ToyEmbedder().embed_bytes(await file.read())
    vec='['+','.join(f'{x:.8f}' for x in q)+']'
    rows=fetch_all(
        """
        select si.structure_key, s.name as structure_name, si.image_url,
               1 - (se.embedding <=> %s::vector) as score
        from structure_embedding se
        join structure_image si on si.id=se.structure_image_id
        join structure s on s.build_id=si.build_id and s.structure_key=si.structure_key
        where si.build_id=%s::uuid
        order by se.embedding <=> %s::vector asc, si.image_url asc
        limit %s
        """,
        (vec,buildId,vec,k)
    )
    return {'matches':rows,'ocr_text':None}
