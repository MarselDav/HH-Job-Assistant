from typing import Annotated

from fastapi import UploadFile, HTTPException, status
from fastapi.params import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel

from api.service import resume_service
from api.dependencies import get_resume_repository, get_resume_analyzer, get_vacancy_repository, get_hh_vacancy_client
from database.repositories.resume_repository import ResumeRepository
from database.repositories.vacancy_repository import VacancyRepository
from hh import hh_vacancy_client
from hh.hh_models import Vacancy
from hh.hh_vacancy_client import HHVacancyClient
from llm.resume_analyzer import ResumeAnalyzer, ResumeAnalysis
from matching.vacancy_retriever import VacancyRetriever
from api.service import resume_service
from api.service import vacancy_service

router = APIRouter()

MAX_LLM_MATCHING_VACANCIES = 5


class MatchingResumeParams(BaseModel):
    resume_id: int
    vacancies_ids: list[int]

async def semantic_matching(
        matching_params: MatchingResumeParams,
        vacancy_repository: VacancyRepository,
        vacancy_retriever : VacancyRetriever,
        resume_repository : ResumeRepository,
        resume_analyzer : ResumeAnalyzer,
        hh_vacancy_client : HHVacancyClient) -> list[Vacancy]:

    resume_id = matching_params.resume_id
    resume = resume_repository.get_by_id(resume_id)

    if resume is None:
        raise ValueError(f"Resume with id={resume_id} not found")

    vacancies_ids = matching_params.vacancies_ids
    vacancies_list = vacancy_repository.get_vacancies_by_ids(vacancies_ids)

    if resume["analysis"] is None:
        await resume_service.analyze_resume(resume_id, resume_repository, resume_analyzer)
        resume = resume_repository.get_by_id(resume_id)

    resume_analysis = ResumeAnalysis(**resume["analysis"])

    for i, vacancy in enumerate(vacancies_list):
        if vacancy.description is None:
            vacancies_list[i].description = await vacancy_service.get_vacancy_description(vacancy.db_id, vacancy_repository, hh_vacancy_client)

    vacancy_retriever.semantic_matching(resume_analysis, vacancies_list)

    return vacancies_list


async def llm_matching(
        matching_params: MatchingResumeParams,
        vacancy_repository: VacancyRepository,
        vacancy_retriever : VacancyRetriever,
        resume_repository : ResumeRepository,
        resume_analyzer : ResumeAnalyzer,
        hh_vacancy_client : HHVacancyClient) -> list[Vacancy]:

    resume_id = matching_params.resume_id
    resume = resume_repository.get_by_id(resume_id)

    if resume is None:
        raise ValueError(f"Resume with id={resume_id} not found")

    vacancies_ids = matching_params.vacancies_ids

    if len(vacancies_ids) > MAX_LLM_MATCHING_VACANCIES:
        raise ValueError("Too many vacancies to match")

    vacancies_list = vacancy_repository.get_vacancies_by_ids(vacancies_ids)

    if resume["analysis"] is None:
        await resume_service.analyze_resume(resume_id, resume_repository, resume_analyzer)
        resume = resume_repository.get_by_id(resume_id)

    resume_analysis = ResumeAnalysis(**resume["analysis"])

    for i, vacancy in enumerate(vacancies_list):
        if vacancy.description is None:
            vacancies_list[i].description = await vacancy_service.get_vacancy_description(vacancy.db_id, vacancy_repository, hh_vacancy_client)

    vacancy_retriever.llm_matching(resume_analysis, vacancies_list)

    return vacancies_list