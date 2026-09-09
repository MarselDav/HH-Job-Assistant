from pprint import pprint

from database.connection import DatabaseConnection
from database.repositories.vacancy_repository import VacancyRepository
from hh.hh_models import VacancySearchFilters, Area
from hh.hh_vacancy_client import HHVacancyClient
from llm.resume_analyzer import ResumeAnalyzer
from llm.llm_client import LLMClient
from llm.cover_letter_generator import CoverLetterGenerator

from matching.vacancy_retriever import VacancyRetriever
from sentence_transformers import SentenceTransformer

from application.job_assistant import JobAssistant
from database.repositories.vacancy_repository import VacancyRepository
from database.repositories.matching_results_repository import MatchingResultsRepository

if __name__ == "__main__":
    vsf = VacancySearchFilters(
        text="C++",
        area=[Area("Москва", ""), Area("Санкт-Петербург", "")],
        experience=["Нет опыта"],
        work_format=["Удалённо"],
    )

    with open("resume_example.txt", "r", encoding="utf-8") as f:
        resume_str = f.read()

    hh_vacancy_client = HHVacancyClient("hh/hh_filters.json")
    llm_client = LLMClient()
    resume_analyzer = ResumeAnalyzer(llm_client)
    embedding_model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    vacancy_retriever = VacancyRetriever(embedding_model,
                          llm_client,
                          0.6,
                          0.4,
                          0.7,
                          1)


    cover_letter_generator = CoverLetterGenerator(llm_client)

    db_connection = DatabaseConnection()
    vacancy_repository = VacancyRepository(db_connection.get_connection())
    matching_results_repository = MatchingResultsRepository(db_connection.get_connection())

    job_assistant = JobAssistant(
        resume_str,
        hh_vacancy_client,
        llm_client,
        resume_analyzer,
        vacancy_retriever,
        cover_letter_generator,
        vacancy_repository,
        matching_results_repository
    )

    vacancy_list = job_assistant.find_suitable_vacancies(vsf)
    pprint(vacancy_list, indent=4)

"""
database/
│
├── schema.sql             ← CREATE TABLE
│
├── init_db.py             ← один раз применяет schema.sql
│
├── connection.py          ← подключение к PostgreSQL
│
├── queries/
│   ├── resumes/
│   │   ├── create.sql
│   │   ├── get_by_id.sql
│   │   └── update_analysis.sql
│   │
│   ├── vacancies/
│   │   ├── create.sql
│   │   ├── get_by_hh_id.sql
│   │   └── get_all.sql
│   │
│   └── matching/
│       ├── create.sql
│       └── get_best.sql
│
└── repositories/
    ├── resume_repository.py
    ├── vacancy_repository.py
    └── matching_repository.py
"""