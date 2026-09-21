from dataclasses import dataclass
from pydantic import BaseModel

class Area(BaseModel):
    category : str
    area : str

class ProfessionalRole(BaseModel):
    category : str
    role : str

class Industry(BaseModel):
    category : str
    industry : str


class VacancySearchFilters(BaseModel):
    text: str | None = None
    area: list[Area] | None = None
    experience: list[str] | None = None
    professional_role: list[ProfessionalRole] | None = None
    industries: list[Industry] | None = None
    employment_form: list[str] | None = None
    work_format: list[str] | None = None
    working_hours: list[str] | None = None
    work_schedule_by_days: list[str] | None = None
    salary: dict | None = None
    currency: str | None = None


class Vacancy(BaseModel):
    db_id : int | None = None
    id: int | None = None
    name: str | None = None
    work_schedule: str | None = None
    response_letter_required: bool | None = None
    company_id: int | None = None
    company_name: str | None = None
    area: str | None = None
    experience: str | None = None
    salary: str | None = None
    work_formats: list[str] | None = None
    work_schedule_by_days: list[str] | None = None
    working_hours: list[str] | None = None
    description: str | None = None

    # поля для сортировки вакансий
    bm25_score: float = 0
    embedding_score: float = 0
    llm_score: float = 0
    total_score: float = 0

    """
    Краткое подведение итогов. 
    По каким критериям кандидат подходит, по каким нет?
    """
    recap: str | None = None
