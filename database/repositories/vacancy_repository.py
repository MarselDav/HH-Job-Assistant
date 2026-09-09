import psycopg
from pathlib import Path
from psycopg.rows import dict_row
from typing import LiteralString, cast
from hh.hh_models import Vacancy


class VacancyRepository:
    def __init__(self, connection: psycopg.Connection):
        self.connection = connection

        queries_path = Path(__file__).parent.parent / "queries" / "vacancies"

        self.create_query = cast(
            LiteralString,
            (queries_path / "create.sql").read_text(encoding="utf-8")
        )

        self.get_description_query = cast(
            LiteralString,
            (queries_path / "get_description.sql").read_text(encoding="utf-8")
        )

    def create(self, vacancy: Vacancy) -> int:
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.create_query,
                (
                    vacancy.id,
                    vacancy.name,
                    vacancy.work_schedule,
                    vacancy.response_letter_required,
                    vacancy.company_id,
                    vacancy.company_name,
                    vacancy.area,
                    vacancy.experience,
                    vacancy.salary,
                    vacancy.work_formats,
                    vacancy.work_schedule_by_days,
                    vacancy.working_hours,
                    vacancy.description,
                ),
            )
            vacancy_id = cursor.fetchone()[0]

        return vacancy_id

    def get_description_by_id(self, hh_id: int) -> str:
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.get_description_query,
                (
                    hh_id,
                ),
            )
            description = cursor.fetchone()

        return description[0] if description is not None else None