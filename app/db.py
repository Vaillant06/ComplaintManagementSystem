import psycopg2
import psycopg2.extras
from flask import current_app


# DATABASE QUERY HELPER
def query(sql, params=(), fetchone=False, fetchall=False, commit=False):
    conn = psycopg2.connect(current_app.config["DATABASE_URL"])
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        cur.execute(sql, params)

        result = None
        
        if fetchone:
            result = cur.fetchone()

        elif fetchall:
            result = cur.fetchall()

        if commit:
            conn.commit()

        return result

    finally:
        cur.close()
        conn.close()
