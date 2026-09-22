import json

from llm.llm_client import LLMClient
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class LanguageItem(BaseModel):
    language: str = Field(description="Название языка, например, 'Английский'")
    level: str = Field(description="Уровень владения, например, 'B2'")

class SkillItem(BaseModel):
    skill: str = Field(description="Название навыка")
    level: str = Field(description="Уровень владения, значение в отрезке [0.0, 1.0]")


class ResumeAnalysis(BaseModel):
    skills_sorted_by_level: list[SkillItem] = Field(
        description="Список навыков с уровнями владения ими "
                    "(Уровень определяется на основе опыта работы, проектов, образования и "
                    "повышения квалификации/курсов. В списке обязательно должен быть навык с уровнем 1,"
                    " это означает, что человек владеет им лучше всего)"
    )
    profession_name : str = Field(
        description="Название профессии или желаемой должности."
    )
    experience: Literal["noExperience", "between1And3", "between3And6", "moreThan6"] = Field(
        description="Опыт работы кандидата. Выберите строго один подходящий вариант."
    )
    languages_with_level : list[LanguageItem] = Field(
        description="Список языков с уровнями владения",
    )
    work_formats: list[Literal[
        "ON_SITE", "REMOTE",
        "HYBRID", "FIELD_WORK"
    ]] = Field(
        description="Существующие варианты работы, "
                    "выберите все подходящие варианты",
        default=["ON_SITE", "REMOTE", "HYBRID", "FIELD_WORK"])
    work_schedule_by_days: list[Literal[
        "SIX_ON_ONE_OFF","FIVE_ON_TWO_OFF",
        "FOUR_ON_FOUR_OFF","FOUR_ON_THREE_OFF",
        "FOUR_ON_TWO_OFF","THREE_ON_THREE_OFF",
        "THREE_ON_TWO_OFF","TWO_ON_TWO_OFF",
        "TWO_ON_ONE_OFF","ONE_ON_THREE_OFF",
        "ONE_ON_TWO_OFF","WEEKEND",
        "FLEXIBLE","OTHER"
    ]] = Field(
        description="Возможные графики работы по дням. "
                    "Выберите один или несколько подходящих вариантов.",
        default=["FIVE_ON_TWO_OFF"]
    )
    working_hours: list[Literal[
        "HOURS_2", "HOURS_3",
        "HOURS_4", "HOURS_6",
        "HOURS_5", "HOURS_7",
        "HOURS_8", "HOURS_9",
        "HOURS_10", "HOURS_11",
        "HOURS_12", "HOURS_24",
        "FLEXIBLE", "OTHER"
    ]] = Field(
        description="Количество рабочих часов в день. "
                    "Выберите все упомянутые или подходящие варианты.",
        default=["HOURS_8"]
    )
    brief_description : str = Field(
        description="Краткое описание профиля кандидата на основе резюме."
    )


class ResumeAnalyzer:
    def __init__(self, llm_client : LLMClient):
        self.llm_client = llm_client

    def analyze(self, resume_str : str) -> ResumeAnalysis:
        prompt=f"""
            Проанализируй резюме кандидата.
            
            Извлеки информацию строго в соответствии с заданной структурой.
            
            Резюме:
            
            {resume_str}
        """

        return self.llm_client.generate(prompt=prompt, response_schema=ResumeAnalysis)


if __name__ == "__main__":
    with open("../resume_example.txt", "r", encoding="utf-8") as f:
        resume_str = f.read()

    # print(json.dumps(ResumeAnalysis.model_json_schema(), indent=2, ensure_ascii=False))

    analyzer = ResumeAnalyzer(llm_client=LLMClient())
    response = analyzer.analyze(resume_str)


    print(response)