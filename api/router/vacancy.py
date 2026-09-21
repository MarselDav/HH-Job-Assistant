from typing import Annotated

from fastapi import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter

from api.service import vacancy_service
from api.dependencies import get_hh_vacancy_client, get_vacancy_repository
from database.repositories.vacancy_repository import VacancyRepository
from hh.hh_models import VacancySearchFilters, Vacancy

from hh.hh_vacancy_client import HHVacancyClient

router = APIRouter()

HHVacancyClientDep = Annotated[HHVacancyClient, Depends(get_hh_vacancy_client)]
VacancyRepositoryDep = Annotated[VacancyRepository, Depends(get_vacancy_repository)]


@router.post("/get_vacancies/", response_model=list[Vacancy])
async def get_vacancies(filters: VacancySearchFilters,
                      vacancy_repository : VacancyRepositoryDep,
                      hh_vacancy_client : HHVacancyClientDep):
    return await vacancy_service.get_vacancies(filters, vacancy_repository, hh_vacancy_client)


@router.get("/get_vacancy_description/")
async def get_vacancy_description(vac_id: int,
                      vacancy_repository : VacancyRepositoryDep,
                      hh_vacancy_client : HHVacancyClientDep):
    return await vacancy_service.get_vacancy_description(vac_id, vacancy_repository, hh_vacancy_client)

"""
Запрос вакансий -> вакансии с id
запрос описания по id -> описание
запрос сортировки по соответствию по id вакансий
"""