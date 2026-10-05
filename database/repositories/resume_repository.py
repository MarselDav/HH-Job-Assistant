import psycopg
from pathlib import Path
from psycopg.rows import dict_row
from typing import LiteralString, cast
from database.connection import DatabaseConnection
from llm.resume_analyzer import ResumeAnalysis
from psycopg.types.json import Jsonb


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

        self.get_resumes_query = cast(
            LiteralString,
            (queries_path / "get_resumes.sql").read_text(encoding="utf-8")
        )

        self.delete_resume_query = cast(
            LiteralString,
            (queries_path / "delete_resume.sql").read_text(encoding="utf-8")
        )

        self.update_query = cast(
            LiteralString,
            (queries_path / "update.sql").read_text(encoding="utf-8")
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

    def get_resumes_by_ids(self, db_ids: list[int]) -> dict:
        with self.database.get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    self.get_resumes_query,
                    (
                        db_ids,
                    )
                )
                resumes_dicts = cursor.fetchall()
                return resumes_dicts

    def delete_resume(self, db_id : int) -> int | None:
        with self.database.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    self.delete_resume_query,
                    (
                        db_id,
                    )
                )
                deleted_resume_id = cursor.fetchone()
                return deleted_resume_id

    def update_analysis(self, resume_id: int, analysis: ResumeAnalysis):
        with self.database.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    self.update_query,
                    (
                        Jsonb(analysis.model_dump()),
                        resume_id,
                    ),
                )
                result = cursor.fetchone()

                return result[0] if result else None