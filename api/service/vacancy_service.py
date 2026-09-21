from database.repositories.vacancy_repository import VacancyRepository
from hh.hh_models import VacancySearchFilters, Vacancy
from hh.hh_vacancy_client import HHVacancyClient


async def get_vacancies(filters: VacancySearchFilters,
                      vacancy_repository : VacancyRepository,
                      hh_vacancy_client : HHVacancyClient) -> list[Vacancy]:

    vacancies_list = hh_vacancy_client.search(filters)

    for i, vacancy in enumerate(vacancies_list):
        db_id = vacancy_repository.create(vacancy)
        vacancies_list[i].db_id = db_id

    return vacancies_list


async def get_vacancy_description(vac_id: int,
                      vacancy_repository : VacancyRepository,
                      hh_vacancy_client : HHVacancyClient) -> str:
    hh_id, description = vacancy_repository.get_description_by_id(vac_id)

    if hh_id is None:
        raise ValueError("There is no vacancy with that id in DB")

    if description is not None:
        return description

    description = hh_vacancy_client.get_vacancy_description(hh_id)
    vacancy_repository.upgrade_description(vac_id, description)
    return description