from llm.llm_client import LLMClient
from pydantic import BaseModel, Field, ConfigDict
from hh.hh_models import Vacancy

class CoverLetter(BaseModel):
    letter: str = Field(
        description="Текст сопроводительного письма"
    )

class CoverLetterGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def get_letter(self, vacancy: Vacancy, resume : str) -> CoverLetter:
        prompt = f"""
                    Напиши сопроводительное письмо на позицию {vacancy.name}
                    
                    Для этого проанализируй описание вакансии:
                    {vacancy.description}
                    
                    И моё резюме:

                    {resume}
                """

        return self.llm_client.generate(prompt=prompt, response_schema=CoverLetter)