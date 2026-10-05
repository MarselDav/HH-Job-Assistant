from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.connection import DatabaseConnection
from database.repositories.company_repository import CompanyRepository
from hh.hh_vacancy_client import HHVacancyClient, HHVacancyFormatter
from hh.hh_filters import HHFilters
from llm.resume_analyzer import ResumeAnalyzer
from llm.llm_client import LLMClient
from llm.cover_letter_generator import CoverLetterGenerator

from matching.vacancy_retriever import VacancyRetriever
from sentence_transformers import SentenceTransformer

from database.repositories.resume_repository import ResumeRepository
from database.repositories.vacancy_repository import VacancyRepository
from database.repositories.matching_results_repository import MatchingResultsRepository

from api.router.resume import router as resume_router
from api.router.vacancy import router as vacancy_router
from api.router.matching import router as matching_router
from api.router.cover_letter import router as cover_letter_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.hh_filters = HHFilters("hh/hh_filters.json")
    app.state.hh_vacancy_formatter = HHVacancyFormatter(app.state.hh_filters)
    app.state.hh_vacancy_client = HHVacancyClient(app.state.hh_filters)
    app.state.llm_client = LLMClient("gemini-3.1-flash-lite") # gemini-3.1-flash-lite
    app.state.resume_analyzer = ResumeAnalyzer(app.state.llm_client)

    app.state.embedding_model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    app.state.vacancy_retriever = VacancyRetriever(app.state.embedding_model,
                                         app.state.llm_client,
                                         0.6,
                                         0.4,
                                         0.7,
                                         1)

    app.state.cover_letter_generator = CoverLetterGenerator(app.state.llm_client)

    app.state.db_connection = DatabaseConnection()
    app.state.resume_repository = ResumeRepository(app.state.db_connection)
    app.state.vacancy_repository = VacancyRepository(app.state.db_connection)
    app.state.company_repository = CompanyRepository(app.state.db_connection)
    app.state.matching_results_repository = MatchingResultsRepository(app.state.db_connection)

    try:
        yield
    finally:
        app.state.db_connection.close()

app = FastAPI(
    title="HH-Job-Assistant",
    lifespan=lifespan
)

app.include_router(resume_router, tags=["resume"])
app.include_router(vacancy_router, tags=["vacancy"])
app.include_router(matching_router, tags=["matching"])
app.include_router(cover_letter_router, tags=["cover_letter"])