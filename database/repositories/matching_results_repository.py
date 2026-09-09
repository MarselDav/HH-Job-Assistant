import psycopg
from pathlib import Path
from psycopg.rows import dict_row
from typing import LiteralString, cast
from hh.hh_models import Vacancy
from matching.vacancy_retriever import MatchingAnalysis


class MatchingResultsRepository:
    def __init__(self, connection: psycopg.Connection):
        self.connection = connection

        queries_path = Path(__file__).parent.parent / "queries" / "matching_results"

        self.create_query = cast(
            LiteralString,
            (queries_path / "create.sql").read_text(encoding="utf-8")
        )

        self.get_query = cast(
            LiteralString,
            (queries_path / "get.sql").read_text(encoding="utf-8")
        )

    def create(self, vacancy: Vacancy, matching_analysis : MatchingAnalysis) -> int:
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.create_query,
                (
                    vacancy.id,
                    vacancy.bm25_score,
                    vacancy.embedding_score,
                    vacancy.llm_score,
                    vacancy.total_score,
                    matching_analysis.matched_skills,
                    matching_analysis.recap,
                ),
            )
            result_id = cursor.fetchone()[0]

        return result_id

    def get_by_ids(self, vacancy_id: int) -> dict:
        with self.connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                self.get_query,
                (
                    vacancy_id,
                ),
            )
            matching_result = cursor.fetchone()

        return matching_result[0] if matching_result is not None else None