import psycopg
from pathlib import Path
from psycopg.rows import dict_row
from typing import LiteralString, cast
from hh.hh_models import Vacancy
from database.connection import DatabaseConnection


class VacancyRepository:
    def __init__(self, database : DatabaseConnection):
        self.database = database

        queries_path = Path(__file__).parent.parent / "queries" / "vacancies"

        self.create_query = cast(
            LiteralString,
            (queries_path / "create.sql").read_text(encoding="utf-8")
        )

        self.get_description_query = cast(
            LiteralString,
            (queries_path / "get_description.sql").read_text(encoding="utf-8")
        )

        self.update_description_query = cast(
            LiteralString,
            (queries_path / "update_description.sql").read_text(encoding="utf-8")
        )

        self.get_vacancies_query = cast(
            LiteralString,
            (queries_path / "get_vacancies.sql").read_text(encoding="utf-8")
        )

    def create(self, vacancy: Vacancy) -> int:
        with self.database.get_connection() as connection:
            with connection.cursor() as cursor:
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

    def get_description_by_id(self, db_id: int) -> tuple[int | None, str | None]:
        with self.database.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    self.get_description_query,
                    (
                        db_id,
                    ),
                )
                description = cursor.fetchone()

                if description is None:
                    return None, None

                return description[0], description[1]

    def upgrade_description(self, id : int, description : str) -> int:
        with self.database.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    self.update_description_query,
                    (
                        description,
                        id,
                    ),
                )
                id = cursor.fetchone()
                return id[0] if id is not None else None


    def get_vacancies_by_ids(self, db_ids: list[int]) -> list[Vacancy]:
        with self.database.get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    self.get_vacancies_query,
                    (
                        db_ids,
                    )
                )
                vacancies_dicts = cursor.fetchall()
                return [Vacancy(**row) for row in vacancies_dicts]