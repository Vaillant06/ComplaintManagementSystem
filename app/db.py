import psycopg2
import psycopg2.extras
from flask import current_app

def query(sql, params=(), fetchone=False, fetchall=False, commit=False):
    conn = psycopg2.connect(current_app.config["DATABASE_URL"])
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        cur.execute(sql, params)

        if commit:
            conn.commit()

        if fetchone:
            return cur.fetchone()

        if fetchall:
            return cur.fetchall()

    finally:
        cur.close()
        conn.close()
