from fastapi import Request

from database.repositories.resume_repository import ResumeRepository
from database.repositories.vacancy_repository import VacancyRepository
from hh.hh_vacancy_client import HHVacancyClient
from llm.cover_letter_generator import CoverLetterGenerator
from llm.resume_analyzer import ResumeAnalyzer
from matching.vacancy_retriever import VacancyRetriever


def get_resume_repository(request : Request) -> ResumeRepository:
    return request.app.state.resume_repository

def get_resume_analyzer(request : Request) -> ResumeAnalyzer:
    return request.app.state.resume_analyzer

def get_hh_vacancy_client(request : Request) -> HHVacancyClient:
    return request.app.state.hh_vacancy_client

def get_vacancy_repository(request : Request) -> VacancyRepository:
    return request.app.state.vacancy_repository

def get_vacancy_retriever(request : Request) -> VacancyRetriever:
    return request.app.state.vacancy_retriever

def get_cover_letter_generator(request : Request) -> CoverLetterGenerator:
    return request.app.state.cover_letter_generator