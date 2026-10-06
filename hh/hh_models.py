from dataclasses import dataclass

import psycopg
from psycopg.types.json import Jsonb
from pydantic import BaseModel


class VacancySearchFilters(BaseModel):
    text: str | None = None
    area: list[str] | None = None
    experience: list[str] | None = None
    professional_role: list[str] | None = None
    industry: list[str] | None = None
    employment_form: list[str] | None = None
    work_format: list[str] | None = None
    working_hours: list[str] | None = None
    work_schedule_by_days: list[str] | None = None
    salary: dict | None = None

class Company(BaseModel):
    db_id : int | None = None
    id: int | None = None
    name: str | None = None
    description : str | None = None
    logo: str | None = None
    site_url: str | None = None

class MatchingResult(BaseModel):
    bm25_score: float = 0
    embedding_score: float = 0
    llm_score: float = 0
    total_score: float = 0

    """
    Краткое подведение итогов.
    По каким критериям кандидат подходит, по каким нет?
    """
    recap: str | None = None

class WorkParameters(BaseModel):
    work_formats: list[str] | None = None
    work_schedule_by_days: list[str] | None = None
    working_hours: list[str] | None = None


"""
 'compensation': {'currencyCode': 'RUR',
                  'from': 200000,
                  'gross': True,
                  'mode': 'MONTH',
                  'perModeFrom': 200000},
"""

class SalaryInfo(BaseModel):
    salary: int | None = None
    salary_mode : str | None = None
    currency_code : str | None = None

class Vacancy(BaseModel):
    db_id : int | None = None
    id: int | None = None
    name: str | None = None
    company : Company | None = None
    area: str | None = None
    experience: str | None = None
    response_letter_required: bool | None = None
    salary_info: SalaryInfo | None = None
    work_parameters : WorkParameters | None = None
    description: str | None = None
    matching_result : MatchingResult | None = None

# class Resume(BaseModel):
#     db_id: int
#     name: str
#     raw_text: str
#     analysis: Jsonb
#     created_at: psycopg.Timestamp