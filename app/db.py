import psycopg2
import psycopg2.extras
from flask import current_app, g

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(current_app.config["DATABASE_URL"])
    return g.db

def query(sql, params=(), fetchone=False, fetchall=False, commit=False):
    connection = get_db()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql, params)

    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()

    if commit:
        connection.commit()

    cursor.close()

    return result