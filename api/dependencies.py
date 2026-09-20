from fastapi import Request

from database.repositories.resume_repository import ResumeRepository
from llm.resume_analyzer import ResumeAnalyzer


def get_resume_repository(request : Request) -> ResumeRepository:
    return request.app.state.resume_repository

def get_resume_analyzer(request : Request) -> ResumeAnalyzer:
    return request.app.state.resume_analyzer
