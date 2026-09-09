from pathlib import Path
import psycopg
import psycopg_binary
import os
from dotenv import load_dotenv

schema = Path("schema.sql").read_text(encoding="utf-8")

load_dotenv()

with psycopg.connect(
    host=os.environ['POSTGRES_HOST'],
    port=os.environ['POSTGRES_PORT'],
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
) as conn:
    with conn.cursor() as cursor:
        cursor.execute(schema)