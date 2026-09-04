import json
from pprint import pprint
import requests
from datetime import datetime, timezone

DICTIONARIES_URL = "https://api.hh.ru/dictionaries"
AREAS_URL = "https://api.hh.ru/areas"
INDUSTRIES_URL = "https://api.hh.ru/industries"
PROFESSIONAL_ROLES_URL = "https://api.hh.ru/professional_roles"

DICTIONARIES_PARAMS_LIST = ["experience",
                            "employment_form",
                            "work_format",
                            "working_hours",
                            "work_schedule_by_days",
                            "vacancy_label",
                            "vacancy_search_order"]


class HHFilterParser:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.timeout = 30

    def get_json(self, url):
        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
        )

        response.raise_for_status()
        return response.json()

    @staticmethod
    def parse_dictionaries(dictionaries_response: dict) -> dict:
        dictionaries_dict = {param : {} for param in DICTIONARIES_PARAMS_LIST}

        for key in dictionaries_dict.keys():
            for parameter in dictionaries_response[key]:
                if parameter.get("name") is not None:
                    dictionaries_dict[key][parameter["name"].replace('\xa0', ' ')] = {"id": parameter["id"]}

        # pprint(dictionaries_dict, indent=4, width=100)

        return dictionaries_dict

    @staticmethod
    def parse_profession_roles(professional_roles_response: dict) -> dict:
        professional_roles_dict = {}

        for category in professional_roles_response["categories"]:
            professional_roles_dict[category["name"]] = {"id": category["id"], "roles": {}}

            for role in category["roles"]:
                professional_roles_dict[category["name"]]["roles"][role["name"]] = {"id": role["id"]}

        return professional_roles_dict

    @staticmethod
    def parse_areas(areas_response: list) -> dict:
        areas_dict = {}

        areas_response_russia = next((
            area for area in areas_response
            if area["id"] == "113"), None
        )

        if areas_response_russia is None:
            raise RuntimeError("Отсутствует Россия в areas_response")

        for area in areas_response_russia["areas"]:
            areas_dict[area["name"]] = {"id" : area["id"], "areas" : {}}
            for city in area["areas"]:
                areas_dict[area["name"]]["areas"][city["name"]] = {"id": city["id"]}

        # pprint(areas_dict, indent=4, width=100)

        return areas_dict

    @staticmethod
    def parse_industries(industries_response: list) -> dict:
        industries_dict = {}

        for industry_category in industries_response:
            industries_dict[industry_category["name"]] = {"id": industry_category["id"], "industries": {}}

            for industry in industry_category["industries"]:
                industries_dict[industry_category["name"]]["industries"][industry["name"]] = {"id": industry["id"]}

        # pprint(industries_dict, indent=4, width=100)

        return industries_dict

    def parse_all(self) -> dict:
        dictionaries = self.parse_dictionaries(self.get_json(DICTIONARIES_URL))
        professional_roles = self.parse_profession_roles(self.get_json(PROFESSIONAL_ROLES_URL))
        areas = self.parse_areas(self.get_json(AREAS_URL))
        industries = self.parse_industries(self.get_json(INDUSTRIES_URL))

        return {
            "meta" : {"generated_at" : datetime.now(timezone.utc).isoformat(timespec="seconds")},
            "dictionaries": dictionaries,
            "professional_roles": professional_roles,
            "areas": areas,
            "industries": industries
        }


    @staticmethod
    def save_filters(filters : dict, path : str) -> None:
        required_sections = {
            "meta",
            "dictionaries",
            "areas",
            "industries",
            "professional_roles"
        }

        for section in required_sections:
            if not filters[section]:
                raise RuntimeError(
                    f"Справочник '{section}' пуст"
                )

        with open(path, "w", encoding="utf-8") as file:
            json.dump(filters, file, ensure_ascii=False, indent=4)


class HHFilters:
    def __init__(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as file:
            self.filters = json.load(file)

    """
    Dictionaries Filters
    """
    def get_dictionaries(self) -> dict:
        return self.filters["dictionaries"]

    def get_dictionaries_categories(self) -> list:
        return self.filters["dictionaries"].keys()

    def get_dictionaries_names(self, category) -> list:
        return self.filters["dictionaries"][category].keys()

    def get_dictionaries_name_id(self, category, name) -> str:
        return self.filters["dictionaries"][category][name]["id"]

    """
    Professional Roles Filters
    """
    def get_profession_roles(self) -> dict:
        return self.filters["professional_roles"]

    def get_professional_roles_categories(self) -> list:
        return list(self.filters["professional_roles"])

    def get_professional_roles_category_id(self, category) -> str:
        return self.filters["professional_roles"][category]["id"]

    def get_professional_roles_category_roles(self, category) -> list:
        return list(self.filters["professional_roles"][category]["roles"])

    def get_professional_roles_id(self, category, name) -> str:
        return self.filters["professional_roles"][category]["roles"][name]["id"]

    """
    Areas Filters
    """
    def get_areas(self) -> dict:
        return self.filters["areas"]

    def get_areas_categories(self) -> list:
        return list(self.filters["areas"])

    def get_areas_category_id(self, category: str) -> str:
        return self.filters["areas"][category]["id"]

    def get_areas_category_areas(self, category: str) -> list:
        return list(self.filters["areas"][category])

    def get_areas_id(self, category: str, name: str) -> str:
        return self.filters["areas"][category][name]["id"]

    """
    Industries Filters
    """
    def get_industries(self) -> dict:
        return self.filters["industries"]

    def get_industries_categories(self) -> list:
        return list(self.filters["industries"])

    def get_industries_category_id(self, category) -> str:
        return self.filters["industries"][category]["id"]

    def get_industries_category_industries(self, category) -> list:
        return list(self.filters["industries"][category]["industries"])

    def get_industries_id(self, category, name) -> str:
        return self.filters["industries"][category]["industries"][name]["id"]

    """
    Metadata
    """
    def get_metadata(self) -> dict:
        return self.filters["meta"]


if __name__ == "__main__":
    parser = HHFilterParser()
    filters_ = parser.parse_all()
    parser.save_filters(filters_, "hh_filters.json")

    # filter = HHFilters("hh_filters.json")
    # keys = filter.get_areas_category_areas("Республика Марий Эл")
    # print(keys)