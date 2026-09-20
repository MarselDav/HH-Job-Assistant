import psycopg
from pathlib import Path
from psycopg.rows import dict_row
from typing import LiteralString, cast
from database.connection import DatabaseConnection


class ResumeRepository:
    def __init__(self, database: DatabaseConnection):
        self.database = database

        queries_path = Path(__file__).parent.parent / "queries" / "resume"

        self.create_query = cast(
            LiteralString,
            (queries_path / "create.sql").read_text(encoding="utf-8")
        )

        self.get_query = cast(
            LiteralString,
            (queries_path / "get.sql").read_text(encoding="utf-8")
        )

    def create(self, name: str, raw_text: str) -> int:
        with self.database.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    self.create_query,
                    (
                        name,
                        raw_text
                    ),
                )
                return cursor.fetchone()[0]

    def get_by_id(self, resume_id: int) -> dict:
        with self.database.get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    self.get_query,
                    (
                        resume_id,
                    ),
                )

                return cursor.fetchone()