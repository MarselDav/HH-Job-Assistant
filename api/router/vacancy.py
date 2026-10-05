from typing import Annotated

from fastapi import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter

from api.service import vacancy_service
from api.dependencies import get_hh_vacancy_client, get_vacancy_repository, get_hh_filters, get_hh_vacancy_formatter
from database.repositories.vacancy_repository import VacancyRepository
from hh.hh_filters import HHFilters
from hh.hh_models import VacancySearchFilters, Vacancy

from hh.hh_vacancy_client import HHVacancyClient, HHVacancyFormatter

router = APIRouter()

HHVacancyClientDep = Annotated[HHVacancyClient, Depends(get_hh_vacancy_client)]
VacancyRepositoryDep = Annotated[VacancyRepository, Depends(get_vacancy_repository)]
HHFiltersDep = Annotated[HHFilters, Depends(get_hh_filters)]
HHVacancyFormatterDep = Annotated[HHVacancyFormatter, Depends(get_hh_vacancy_formatter)]


@router.post("/get_vacancies/", response_model=list[Vacancy])
async def get_vacancies(filters: VacancySearchFilters,
                      vacancy_repository : VacancyRepositoryDep,
                      hh_vacancy_client : HHVacancyClientDep,
                      hh_vacancy_formatter :  HHVacancyFormatterDep):
    return await vacancy_service.get_vacancies(filters, vacancy_repository,
                                               hh_vacancy_client, hh_vacancy_formatter)


@router.get("/get_vacancy_description/")
async def get_vacancy_description(vac_id: int,
                      vacancy_repository : VacancyRepositoryDep,
                      hh_vacancy_client : HHVacancyClientDep):
    return await vacancy_service.get_vacancy_description(vac_id, vacancy_repository, hh_vacancy_client)

@router.get("/get_vacancy_search_filters/")
async def get_vacancy_search_filters(hh_filters : HHFiltersDep):
    return await vacancy_service.get_vacancy_search_filters(hh_filters)