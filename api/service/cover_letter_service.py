from fastapi import APIRouter

from database.repositories.resume_repository import ResumeRepository
from database.repositories.vacancy_repository import VacancyRepository
from hh.hh_models import Vacancy
from llm.cover_letter_generator import CoverLetterGenerator, CoverLetter
from typing import Annotated
from api.dependencies import get_cover_letter_generator
from fastapi import Depends


async def get_cover_letter(vacancy_id: int,
                           resume_id: int,
                           resume_repository: ResumeRepository,
                           vacancy_repository: VacancyRepository,
                           cover_letter_generator : CoverLetterGenerator) -> CoverLetter:

    vacancy = vacancy_repository.get_vacancies_by_ids([vacancy_id])[0]

    if vacancy is None:
        raise ValueError(f"No vacancy with id={vacancy_id} found")

    resume = resume_repository.get_by_id(resume_id)

    if resume is None:
        raise ValueError(f"No resume with id={resume_id} found")

    if resume["raw_text"] is None or resume["raw_text"] == "":
        raise ValueError(f"No text in resume with id={resume_id}")

    return cover_letter_generator.get_letter(vacancy, resume["raw_text"])