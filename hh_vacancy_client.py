import re
import html
import json
from dataclasses import asdict

from hh_models import VacancySearchFilters, Area, Vacancy, ProfessionalRole, Industry
from hh_filters import HHFilters, DICTIONARIES_PARAMS_LIST
import requests
from bs4 import BeautifulSoup

VACANCY_URL = "https://hh.ru/search/vacancy"
VACANCY_DETAILS_URL = "https://hh.ru/vacancy/{}"

class HHVacancyClient:
    def __init__(self, filters_json_path: str) -> None:
        self.hh_filters = HHFilters(filters_json_path)

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
            if vacancy.id is not None and vacancy.description is not None:
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
        vacancy_search_filters = {
            key: value
            for key, value in asdict(filters).items()
            if value is not None
        }

        if vacancy_search_filters.get("area") is not None:
            for area_idx in range(len(vacancy_search_filters["area"])):
                area = vacancy_search_filters["area"][area_idx]
                if len(area["area"]) == 0:
                    vacancy_search_filters["area"][area_idx] = self.hh_filters.get_areas_category_id(area["category"])
                else:
                    vacancy_search_filters["area"][area_idx] = self.hh_filters.get_areas_id(
                        area["category"],
                        area["area"]
                    )

        if vacancy_search_filters.get("professional_role") is not None:
            for prof_role_idx in range(len(vacancy_search_filters["professional_role"])):
                professional_role = vacancy_search_filters["professional_role"][prof_role_idx]
                vacancy_search_filters["professional_role"][prof_role_idx] = self.hh_filters.get_professional_roles_id(
                        professional_role["category"],
                        professional_role["role"]
                    )

        if vacancy_search_filters.get("industries") is not None:
            for industries_idx in range(len(vacancy_search_filters["industries"])):
                industries = vacancy_search_filters["industries"][industries_idx]
                vacancy_search_filters["industries"][industries_idx] = self.hh_filters.get_industries_id(
                    industries["category"], industries["industry"])

        for param in DICTIONARIES_PARAMS_LIST:
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

    def _parse_search_response(self, page : str) -> list[Vacancy]:
        pattern = re.compile(
            r'<template[^>]*id="HH-Lux-InitialState"[^>]*>(.*?)</template>',
            re.DOTALL,
        )
        match = pattern.search(page)

        if not match:
            raise RuntimeError("HH-Lux-InitialState not found")

        raw_json = match.group(1)
        decoded_json = html.unescape(raw_json)
        data = json.loads(decoded_json)

        vacancies_list : list[Vacancy] = list()

        print("JSON successfully parsed!")
        vacancies = data["vacancySearchResult"]["vacancies"]
        print("Vacancies:", len(vacancies))

        for vacancy in vacancies:
            vacancies_list.append(Vacancy(
                id=vacancy.get("vacancyId"),
                name=vacancy.get("name"),
                work_schedule=vacancy.get("@workSchedule"),
                response_letter_required=vacancy.get("@responseLetterRequired"),
                company_id=vacancy.get("company", {}).get("id"),
                company_name=vacancy.get("company", {}).get("name"),
                area=vacancy.get("area", {}).get("name"),
                experience=vacancy.get("workExperience"),
                salary=vacancy.get("salary"),
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
                ),
                description = None
            ))

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
    vsf = VacancySearchFilters(
        text="C++",
        area=[Area("Москва", ""), Area("Санкт-Петербург", "")],
        experience=["Нет опыта"],
        work_format=["Удалённо"],
    )

    hh = HHVacancyClient("hh_filters.json")
    vac_list = hh.search(vsf)
    hh.load_descriptions(vac_list)

    print(vac_list)