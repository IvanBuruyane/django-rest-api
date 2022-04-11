import psycopg2
import time
from django.db.utils import OperationalError
from sys import stdout
from django.db import connections
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def run_sql(sql):
    conn = psycopg2.connect(database="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(sql)
    conn.close()


def wait_for_db():
    stdout.write("Waiting for database...")
    db_connection = None
    time.sleep(5)
    while not db_connection:
        try:
            db_connection = connections["default"]
        except OperationalError:
            stdout.write("Database unavailable, waiting 1 second...")
            time.sleep(1)

    stdout.write("Database available!")
