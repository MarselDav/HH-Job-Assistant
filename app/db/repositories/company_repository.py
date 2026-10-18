import psycopg
from pathlib import Path
from psycopg.rows import dict_row
from typing import LiteralString, cast
from hh.hh_models import Company
from database.connection import DatabaseConnection


class CompanyRepository:
    def __init__(self, database : DatabaseConnection):
        self.database = database

        queries_path = Path(__file__).parent.parent / "queries" / "companies"

        self.create_query = cast(
            LiteralString,
            (queries_path / "create.sql").read_text(encoding="utf-8")
        )

    def create(self, company: Company) -> int:
        with self.database.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    self.create_query,
                    (
                        company.id,
                        company.name,
                        company.description,
                        company.logo,
                        company.site_url
                    ),
                )
                company_id = cursor.fetchone()[0]
                return company_id