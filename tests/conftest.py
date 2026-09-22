import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from database.repositories.resume_repository import ResumeRepository
from api.dependencies import get_resume_repository, get_resume_analyzer

from api.app import app
from llm.resume_analyzer import ResumeAnalyzer


@pytest.fixture
def mock_resume_repository():
    return MagicMock(spec=ResumeRepository)

@pytest.fixture
def mock_resume_analyzer():
    return MagicMock(spec=ResumeAnalyzer)

@pytest.fixture
def test_resume_client(mock_resume_repository, mock_resume_analyzer):
    app.dependency_overrides[get_resume_repository] = lambda: mock_resume_repository
    app.dependency_overrides[get_resume_analyzer] = lambda: mock_resume_analyzer

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
