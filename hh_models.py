from dataclasses import dataclass

@dataclass(frozen=True)
class Area:
    category : str
    area : str

@dataclass(frozen=True)
class ProfessionalRole:
    category : str
    role : str

@dataclass(frozen=True)
class Industry:
    category : str
    industry : str

@dataclass(kw_only=True)
class VacancySearchFilters:
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


@dataclass
class Vacancy:
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