from contextlib import contextmanager

import psycopg
from psycopg_pool import ConnectionPool
import os
from dotenv import load_dotenv

class DatabaseConnection:
    def __init__(self):
        load_dotenv()

        self.pool = ConnectionPool(
            conninfo=(
                f"host={os.environ['POSTGRES_HOST']} "
                f"port={os.environ['POSTGRES_PORT']} "
                f"dbname={os.environ['POSTGRES_DB']} "
                f"user={os.environ['POSTGRES_USER']} "
                f"password={os.environ['POSTGRES_PASSWORD']}"
            ),
            min_size=1,
            max_size=10,
        )

    @contextmanager
    def get_connection(self):
        with self.pool.connection() as connection:
            try:
                yield connection
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    def close(self):
        self.pool.close()