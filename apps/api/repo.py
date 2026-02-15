from typing import Any
from .db import get_conn


def fetch_all(sql:str, params:tuple[Any,...]=()):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        cols=[d.name for d in cur.description]
        return [dict(zip(cols,row)) for row in cur.fetchall()]


def fetch_one(sql:str, params:tuple[Any,...]=()):
    rows=fetch_all(sql,params)
    if not rows:
        raise KeyError('not found')
    return rows[0]
