from dataclasses import dataclass

from database.repositories.matching_results_repository import MatchingResultsRepository
from database.repositories.vacancy_repository import VacancyRepository
from hh.hh_models import VacancySearchFilters, Area, Vacancy
from hh.hh_vacancy_client import HHVacancyClient
from llm.resume_analyzer import ResumeAnalyzer, ResumeAnalysis
from llm.llm_client import LLMClient
from llm.cover_letter_generator import CoverLetterGenerator

from matching.vacancy_retriever import VacancyRetriever
from sentence_transformers import SentenceTransformer


class JobAssistant:
    def __init__(self,
                 resume_str,
                 hh_vacancy_client: HHVacancyClient,
                 llm_client: LLMClient,
                 resume_analyzer: ResumeAnalyzer,
                 vacancy_retriever : VacancyRetriever,
                 cover_letter_generator: CoverLetterGenerator,
                 vacancy_repository: VacancyRepository,
                 matching_results_repository: MatchingResultsRepository):

        self.resume_str = resume_str
        self.hh_vacancy_client = hh_vacancy_client
        self.llm_client = llm_client
        self.resume_analyzer = resume_analyzer
        self.vacancy_retriever = vacancy_retriever
        self.cover_letter_generator = cover_letter_generator

        self.vacancy_repository = vacancy_repository
        self.matching_results_repository = matching_results_repository

    def load_descriptions_from_db(self, vacancies_list : list[Vacancy]):
        for vacancy in vacancies_list:
            if vacancy.id is not None and vacancy.description is None:
                vacancy.description = self.vacancy_repository.get_description_by_id(vacancy.id)


    def load_matching_from_db(self, vacancies_list : list[Vacancy]):
        for vacancy in vacancies_list:
            matching_result = self.matching_results_repository.get_by_ids(vacancy.id)

            if matching_result is not None:
                vacancy.bm25_score = matching_result["bm25_score"]
                vacancy.embedding_score = matching_result["embedding_score"]
                vacancy.llm_score = matching_result["llm_score"]
                vacancy.total_score = matching_result["total_score"]
                vacancy.recap = matching_result["recap"]

    def find_suitable_vacancies(self, vsf : VacancySearchFilters) -> list[Vacancy]:
        vacancies_list = self.hh_vacancy_client.search(vsf)
        self.load_descriptions_from_db(vacancies_list) # подгружаем описание для существующих в бд вакансий
        self.hh_vacancy_client.load_descriptions(vacancies_list)

        resume_analysis = self.resume_analyzer.analyze(self.resume_str)
        self.load_matching_from_db(vacancies_list)
        self.vacancy_retriever.retrieve(resume_analysis, vacancies_list)

        return vacancies_list

    def get_cover_letter(self, vacancy: Vacancy, resume : str):
        return self.cover_letter_generator.get_letter(vacancy, resume)