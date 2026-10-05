from database.repositories.company_repository import CompanyRepository
from database.repositories.vacancy_repository import VacancyRepository
from hh.hh_filters import HHFilters
from hh.hh_models import VacancySearchFilters, Vacancy
from hh.hh_vacancy_client import HHVacancyClient, HHVacancyFormatter


async def get_vacancies(
            filters: VacancySearchFilters,
            vacancy_repository : VacancyRepository,
            company_repository : CompanyRepository,
            hh_vacancy_client : HHVacancyClient,
            hh_vacancy_formatter : HHVacancyFormatter) -> list[Vacancy]:

    vacancies_list = hh_vacancy_client.search(filters)

    for i, vacancy in enumerate(vacancies_list):
        company_db_id = company_repository.create(vacancy.company)
        vacancies_list[i].company.db_id = company_db_id

        vacancy_db_id = vacancy_repository.create(vacancy)
        vacancies_list[i].db_id = vacancy_db_id

    hh_vacancy_formatter.make_humanreadable_vacancies(vacancies_list)

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


async def get_vacancy_search_filters(hh_filters : HHFilters) -> dict[str, dict[str, list]]:
    return hh_filters.get_simplify_filters()