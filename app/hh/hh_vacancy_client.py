import re
import html
import json
from dataclasses import asdict

from hh.hh_models import VacancySearchFilters, Vacancy, Company, SalaryInfo, WorkParameters
from hh.hh_filters import HHFilters, DICTIONARIES_PARAMS_DICT
import requests
from bs4 import BeautifulSoup

VACANCY_URL = "https://hh.ru/search/vacancy"
VACANCY_DETAILS_URL = "https://hh.ru/vacancy/{}"
ORIGINAL_LOGO_TYPE = 'ORIGINAL'

class HHVacancyClient:
    def __init__(self, hh_filters: HHFilters) -> None:
        self.hh_filters = hh_filters

        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.timeout = 30

    def search(self, filters : VacancySearchFilters) -> list[Vacancy]:
        params = self._build_search_params(filters)

        response = requests.get(
            VACANCY_URL,
            params=params,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

        vacancies_list = self._parse_search_response(response.text)
        return vacancies_list

    def load_descriptions(self, vacancies_list : list[Vacancy]) -> None:
        for vacancy in vacancies_list:
            if vacancy.id is not None and vacancy.description is None:
                vacancy.description = self.get_vacancy_description(vacancy.id)

    def get_vacancy_description(self, vacancy_id: int) -> str:
        url = VACANCY_DETAILS_URL.format(vacancy_id)

        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return self._parse_vacancy_response(response.text)

    def _build_search_params(self, filters : VacancySearchFilters) -> dict:
        vacancy_search_filters = filters.model_dump()

        if vacancy_search_filters.get("area") is not None:
            areas_list = vacancy_search_filters.get("area")
            for area_idx in range(len(areas_list)):
                vacancy_search_filters["area"][area_idx] = self.hh_filters.get_area_id(
                    areas_list[area_idx])

        if vacancy_search_filters.get("professional_role") is not None:
            roles_list = vacancy_search_filters.get("professional_role")
            for role_idx in range(len(roles_list)):
                vacancy_search_filters["professional_role"][role_idx] = self.hh_filters.get_profession_role_id(
                    roles_list[role_idx])

        if vacancy_search_filters.get("industry") is not None:
            industries_list = vacancy_search_filters.get("industry")
            for industry_idx in range(len(industries_list)):
                vacancy_search_filters["industry"][industry_idx] = self.hh_filters.get_industry_id(
                    industries_list[industry_idx])

        for param in DICTIONARIES_PARAMS_DICT.keys():
            if vacancy_search_filters.get(param) is not None:
                for name_idx in range(len(vacancy_search_filters[param])):
                    vacancy_search_filters[param][name_idx] = self.hh_filters.get_dictionaries_name_id(
                        param,
                        vacancy_search_filters[param][name_idx]
                    )

        return vacancy_search_filters

    @staticmethod
    def _get_elements(data: dict, key: str, element_key: str) -> list[str]:
        items = data.get(key)

        if not items:
            return []

        return items[0].get(element_key, [])

    def _parse_logo_info(self, company_info: dict, _type : str) -> str | None:
        logo_types_list = company_info.get("logos", {}).get('logo')

        if logo_types_list is None:
            return None

        logo = None
        for logo_type in logo_types_list:
            if logo_type.get("@type") == _type:
                logo = logo_type.get("@url")
                break

        if logo is None and _type != ORIGINAL_LOGO_TYPE:
            return self._parse_logo_info(company_info, ORIGINAL_LOGO_TYPE)

        return logo

    @staticmethod
    def _parse_company_name(company_info: dict) -> str | None:
        if company_info.get("name") is not None:
            return company_info.get("name")

        if company_info.get("visibleName") is not None:
            return company_info.get("visibleName")

        return None

    def _parse_company_info(self, company_info) -> Company:
        return Company(
            id=company_info.get("id"),
            name=self._parse_company_name(company_info),
            logo=self._parse_logo_info(company_info, "small"),
            site_url=company_info.get("companySiteUrl"),)

    @staticmethod
    def _parse_salary_info(salary_info) -> SalaryInfo | None:
        if salary_info is None:
            return None

        salary_from = salary_info.get("from")
        salary_to = salary_info.get("to")

        return SalaryInfo(
            salary_from=salary_from,
            salary_to=salary_to,
            salary_mode=salary_info.get("mode"),
            currency=salary_info.get("currencyCode")
        )

    def _parse_work_parameters(self, vacancy) -> WorkParameters:
        return WorkParameters(
                work_formats=self._get_elements(
                    vacancy,
                    "workFormats",
                    "workFormatsElement",
                ),
                work_schedule_by_days=self._get_elements(
                    vacancy,
                    "workScheduleByDays",
                    "workScheduleByDaysElement",
                ),
                working_hours=self._get_elements(
                    vacancy,
                    "workingHours",
                    "workingHoursElement",
                ))

    @staticmethod
    def _parse_vacancy_info(vacancy, company, salary_info, work_parameters) -> Vacancy:
        return Vacancy(
                id=vacancy.get("vacancyId"),
                name=vacancy.get("name"),
                company=company,
                area=vacancy.get("area", {}).get("name"),
                experience=vacancy.get("workExperience"),
                response_letter_required=vacancy.get("@responseLetterRequired"),
                salary_info=salary_info,
                work_parameters=work_parameters,)

    def _parse_search_response(self, page : str) -> list[Vacancy]:
        pattern = re.compile(
            r'<template[^>]*id="HH-Lux-InitialState"[^>]*>(.*?)</template>',
            re.DOTALL,
        )
        match = pattern.search(page)

        if not match:
            raise RuntimeError("[HHVacancyClient][_parse_search_response] "
                               "HH-Lux-InitialState not found")

        raw_json = match.group(1)
        decoded_json = html.unescape(raw_json)
        data = json.loads(decoded_json)

        vacancies_list : list[Vacancy] = list()

        vacancies = data["vacancySearchResult"]["vacancies"]
        print("[HHVacancyClient][_parse_search_response] "
              "JSON parsed! Vacancies count:", len(vacancies))

        # from pprint import pprint
        # pprint(vacancies[0])

        for vacancy in vacancies:
            company = self._parse_company_info(vacancy.get("company", {}))
            salary_info = self._parse_salary_info(vacancy.get("compensation"))
            work_parameters = self._parse_work_parameters(vacancy)
            vacancies_list.append(self._parse_vacancy_info(vacancy,
                                                           company,
                                                           salary_info,
                                                           work_parameters))

        return vacancies_list

    @staticmethod
    def _parse_vacancy_response(page: str) -> str:
        soup = BeautifulSoup(page, "html.parser")
        content_div = soup.find("div", class_=["tmpl_hh_content", "g-user-content"])

        if not content_div:
            print("Нужный блок div не найден")
            return str()

        text = content_div.get_text(separator="\n", strip=True)  # strip - убрать лишние пробелы по краям
        return text

if __name__ == "__main__":
    # pass
    vsf = VacancySearchFilters(
        text="C++ developer",
    )

    hh_filters = HHFilters("hh_filters.json")
    hh = HHVacancyClient(hh_filters)
    vac_list = hh.search(vsf)
    # hh.load_descriptions(vac_list)

    # print(vac_list[0])