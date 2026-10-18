from fastapi import APIRouter

from database.repositories.resume_repository import ResumeRepository
from database.repositories.vacancy_repository import VacancyRepository
from hh.hh_models import Vacancy
from llm.cover_letter_generator import CoverLetterGenerator
from typing import Annotated
from api.dependencies import get_cover_letter_generator, get_resume_repository, get_vacancy_repository
from fastapi import Depends
from api.service import cover_letter_service


router = APIRouter()

ResumeRepositoryDep = Annotated[ResumeRepository, Depends(get_resume_repository)]
VacancyRepositoryDep = Annotated[VacancyRepository, Depends(get_vacancy_repository)]
CoverLetterGeneratorDep = Annotated[CoverLetterGenerator, Depends(get_cover_letter_generator)]

@router.get("/cover_letter/")
async def get_cover_letter(vacancy_id: int,
                           resume_id: int,
                           resume_repository: ResumeRepositoryDep,
                           vacancy_repository: VacancyRepositoryDep,
                           cover_letter_generator : CoverLetterGeneratorDep):
    """
    По хорошему надо добавить pydantic модель для Resume и пересылать её в CoverLetterGenerator
    :return:
    """
    return await cover_letter_service.get_cover_letter(vacancy_id,
                                                       resume_id,
                                                       resume_repository,
                                                       vacancy_repository,
                                                       cover_letter_generator)