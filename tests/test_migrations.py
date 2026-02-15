import psycopg

DB='postgresql://postgres:postgres@localhost:5432/rlc'

def test_schema_tables_exist():
    with psycopg.connect(DB) as conn, conn.cursor() as cur:
        cur.execute("select table_name from information_schema.tables where table_schema='public'")
        names={r[0] for r in cur.fetchall()}
    for t in ['pack_build','entity_item','entity_mob','recipe','structure_embedding']:
        assert t in names
