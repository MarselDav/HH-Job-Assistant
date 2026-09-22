from typing import Annotated

from fastapi import UploadFile, HTTPException, status
from fastapi.params import Depends
from fastapi.routing import APIRouter

from api.service import resume_service
from api.dependencies import get_resume_repository, get_resume_analyzer
from database.repositories.resume_repository import ResumeRepository
from llm.resume_analyzer import ResumeAnalyzer

router = APIRouter()

ResumeRepositoryDep = Annotated[ResumeRepository, Depends(get_resume_repository)]
ResumeAnalyzerDep = Annotated[ResumeAnalyzer, Depends(get_resume_analyzer)]

@router.post("/upload_resume/", status_code=status.HTTP_201_CREATED)
async def upload_resume(file : UploadFile,
                        name : str,
                        resume_repository : ResumeRepositoryDep):

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file was not uploaded"
        )
    try:
        result = await resume_service.upload_resume(file, name, resume_repository)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e)
        )

@router.get("/analyze_resume/{resume_id}", status_code=status.HTTP_201_CREATED)
async def analyze_resume(resume_id : int,
                         resume_repository : ResumeRepositoryDep,
                         resume_analyzer : ResumeAnalyzerDep):
    return await resume_service.analyze_resume(resume_id, resume_repository, resume_analyzer)
