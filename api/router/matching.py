from typing import Annotated

from fastapi import UploadFile, HTTPException, status
from fastapi.params import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel

from api.service import resume_service, matching_service
from api.dependencies import get_resume_repository, get_resume_analyzer, get_vacancy_repository, get_hh_vacancy_client, \
    get_vacancy_retriever
from api.service.matching_service import MatchingResumeParams
from database.repositories.resume_repository import ResumeRepository
from database.repositories.vacancy_repository import VacancyRepository
from hh.hh_models import Vacancy
from hh.hh_vacancy_client import HHVacancyClient
from llm.resume_analyzer import ResumeAnalyzer
from matching.vacancy_retriever import VacancyRetriever

router = APIRouter()


ResumeRepositoryDep = Annotated[ResumeRepository, Depends(get_resume_repository)]
VacancyRepositoryDep = Annotated[VacancyRepository, Depends(get_vacancy_repository)]
VacancyRetrieverDep = Annotated[VacancyRetriever, Depends(get_vacancy_retriever)]
ResumeAnalyzerDep = Annotated[ResumeAnalyzer, Depends(get_resume_analyzer)]
HHVacancyClientDep = Annotated[HHVacancyClient, Depends(get_hh_vacancy_client)]


@router.post("/semantic_matching/", response_model=list[Vacancy])
async def semantic_matching(
        matching_params : MatchingResumeParams,
        vacancy_repository : VacancyRepositoryDep,
        vacancy_retriever : VacancyRetrieverDep,
        resume_repository : ResumeRepositoryDep,
        resume_analyzer : ResumeAnalyzerDep,
        hh_vacancy_client : HHVacancyClientDep,):

    return await matching_service.semantic_matching(
        matching_params, vacancy_repository,
        vacancy_retriever, resume_repository,
        resume_analyzer, hh_vacancy_client)


@router.post("/llm_matching/", response_model=list[Vacancy])
async def llm_matching(
        matching_params : MatchingResumeParams,
        vacancy_repository : VacancyRepositoryDep,
        vacancy_retriever : VacancyRetrieverDep,
        resume_repository : ResumeRepositoryDep,
        resume_analyzer : ResumeAnalyzerDep,
        hh_vacancy_client : HHVacancyClientDep,):

    return await matching_service.llm_matching(
        matching_params, vacancy_repository,
        vacancy_retriever, resume_repository,
        resume_analyzer, hh_vacancy_client)