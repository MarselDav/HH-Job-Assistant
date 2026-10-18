from hh.hh_filters import HHFilters
from hh.hh_models import Vacancy


class HHVacancyFormatter:
    def __init__(self, hh_filters : HHFilters):
        self.hh_filters = hh_filters

    def make_humanreadable_vacancy(self, vacancy : Vacancy):
        if vacancy.experience is not None:
            vacancy.experience = (
                self.hh_filters.get_dictionaries_name(vacancy.experience))

        if vacancy.salary_info is not None:
            currency = vacancy.salary_info.currency
            if currency is not None:
                vacancy.salary_info.currency = self.hh_filters.get_dictionaries_name(currency)

            salary_mode = vacancy.salary_info.salary_mode
            if salary_mode is not None:
                vacancy.salary_info.salary_mode = self.hh_filters.get_dictionaries_name(salary_mode)

        if vacancy.work_parameters is not None:
            work_formats = vacancy.work_parameters.work_formats
            if work_formats is not None:
                vacancy.work_parameters.work_formats = [self.hh_filters.get_dictionaries_name(f)
                                        for f in work_formats]

            work_schedule_by_days = vacancy.work_parameters.work_schedule_by_days
            if work_schedule_by_days is not None:
                vacancy.work_parameters.work_schedule_by_days = [self.hh_filters.get_dictionaries_name(f)
                                        for f in work_schedule_by_days]

            working_hours = vacancy.work_parameters.working_hours
            if working_hours is not None:
                vacancy.work_parameters.working_hours = [self.hh_filters.get_dictionaries_name(f)
                                                 for f in working_hours]

    def make_humanreadable_vacancies(self, vacancies_list : list[Vacancy]):
        for vacancy in vacancies_list:
            self.make_humanreadable_vacancy(vacancy)