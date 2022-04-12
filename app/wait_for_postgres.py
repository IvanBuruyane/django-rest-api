import logging
import os
from time import sleep, time
import psycopg2


def pg_isready():
    check_timeout = 30
    check_interval = 2
    interval_unit = "second" if check_interval == 5 else "seconds"
    config = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "host": os.getenv("DB_HOST"),
    }

    start_time = time()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    while time() - start_time < check_timeout:
        try:
            conn = psycopg2.connect(**config)
            logger.info("Postgres is ready! ✨ 💅")
            conn.close()
            return True
        except psycopg2.OperationalError:
            logger.info(
                f"Postgres isn't ready. Waiting for {check_interval} {interval_unit}..."
            )
            sleep(check_interval)

    logger.error(f"We could not connect to Postgres within {check_timeout} seconds.")
    return False


pg_isready()
