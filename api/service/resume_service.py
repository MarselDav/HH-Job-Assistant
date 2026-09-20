from fastapi import UploadFile

from database.repositories.resume_repository import ResumeRepository
from llm.resume_analyzer import ResumeAnalyzer


async def upload_resume(file : UploadFile, name :str, resume_repository : ResumeRepository) -> dict:
    content_bytes = await file.read()

    try:
        text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("Файл должен быть в кодировки utf-8")

    resume_id = resume_repository.create(name, text)
    return {"resume_id" : resume_id, "text" : text}


async def analyze_resume(resume_id : int,
                         resume_repository : ResumeRepository,
                         resume_analyzer : ResumeAnalyzer) -> dict:

    resume = resume_repository.get_by_id(resume_id)

    resume_analysis = resume_analyzer.analyze(resume["raw_text"])

    return {
        "resume_id" : resume_id,
        "resume_name": resume["name"],
        "resume_analysis": resume_analysis.model_dump_json(),
    }