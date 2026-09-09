from statistics import mean
from sentence_transformers import SentenceTransformer
from hh.hh_filters import HHFilters
from hh.hh_models import Vacancy
from llm.llm_client import LLMClient
from llm.resume_analyzer import ResumeAnalysis
from pydantic import BaseModel, Field
import re

class MatchingAnalysis(BaseModel):
    score : float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Score соответствия вакансии и резюме кандидата. Значение в отрезке [0, 1]."
    )
    matched_skills : list[str] = Field(
        default_factory=list,
        description="Список навыков, по которым подходит кандидат"
    )
    recap: str = Field(
        default='',
        description="Краткое подведение итогов. По каким критериям кандидат подходит, по каким нет?"
    )

"""
передаётся ResumeAnalysis в каждый метод и постоянно преобразуется в текст,
возможно стоит передавать в конструктор один раз
"""
class VacancyRetriever:
    def __init__(self,
                 embedding_model : SentenceTransformer,
                 llm_client : LLMClient,
                 bm25_coef : float, embedding_coef : float,
                 llm_matching_coef : float, vc_llm_matching : float) -> None:

        self.embedding_model = embedding_model
        self.llm_client = llm_client

        self.bm25_coef = bm25_coef
        self.embedding_coef = embedding_coef
        self.llm_matching_coef = llm_matching_coef
        self.vacancy_cnt_for_llm_matching = vc_llm_matching

    # метод изменяет поля bm25_scores у вакансий в vacancies_list и возвращает нормализованный список scores
    def custom_bm25_scores(self, vacancies_list : list[Vacancy], skill_w : dict[str, float], k1=0.6, b=0.4) -> list[float]:
        vacancy_texts = [self._convert_vacancy_to_text(vacancy) for vacancy in vacancies_list]
        average_vacancy_len = mean([len(vacancy_text) for vacancy_text in vacancy_texts])

        skill_weights = self._skill_weights_prepare(skill_w)
        tokenized_vacancy_texts = self._vacancy_texts_prepare(vacancy_texts)
        final_scores_list = []

        for tokenized_vacancy_text in tokenized_vacancy_texts:
            score = 0.0
            for skill, weight in skill_weights.items():
                skill_freq = tokenized_vacancy_text.count(skill)
                denominator = skill_freq + k1 * (1 - b + b *
                                               (len(tokenized_vacancy_text) / average_vacancy_len))
                score +=  weight * skill_freq * (k1 + 1) / denominator

            final_scores_list.append(score)

        normalized_scores = self._normalize_scores(final_scores_list)
        for i, normalized_score in enumerate(normalized_scores):
            vacancies_list[i].bm25_score = normalized_score
            vacancies_list[i].total_score += self.bm25_coef * normalized_score

        return normalized_scores

    # метод изменяет поля embedding_score у вакансий в vacancies_list и возвращает нормализованный список scores
    def embedding_scores(self, resume : ResumeAnalysis, vacancies_list : list[Vacancy]) -> list[float]:
        resume_text = self._convert_resume_to_text(resume)
        vacancy_texts = [self._convert_vacancy_to_text(vacancy) for vacancy in vacancies_list]

        resume_embedding = self.embedding_model.encode_query(
            resume_text,
            convert_to_tensor=True
        )

        vacancy_embedding = self.embedding_model.encode_document(
            vacancy_texts,
            convert_to_tensor=True
        )

        similarities = self.embedding_model.similarity(
            resume_embedding,
            vacancy_embedding
        )

        normalized_scores = self._normalize_scores(similarities[0].tolist())

        for i, normalized_score in enumerate(normalized_scores):
            vacancies_list[i].embedding_score = normalized_score
            vacancies_list[i].total_score += self.embedding_coef * normalized_score

        return normalized_scores

    def llm_matching(self, resume : ResumeAnalysis, vacancy_list : list[Vacancy]):
        for i, vacancy in enumerate(vacancy_list):
            if vacancy.recap is not None:
                continue

            prompt = f"""
                        Проанализируй, насколько хорошо кандидат подходит на эту вакансию.
    
                        Анализ выполни на основе резюме кандидата
    
                        Резюме:
    
                        {self._convert_resume_to_text(resume)}
                        
                        И на основе описания вакансии:
                        
                        {self._convert_vacancy_to_text(vacancy)}
                    """

            matching_response = self.llm_client.generate(prompt=prompt, response_schema=MatchingAnalysis)
            print(f"Оценка соответствия от LLM для вакансии: {vacancy.name}")
            print(matching_response)

            vacancy_list[i].llm_score = matching_response.score
            vacancy_list[i].total_score += self.llm_matching_coef * matching_response.score
            vacancy_list[i].recap = matching_response.recap

    def retrieve(self, resume_analysis : ResumeAnalysis, vacancy_list : list[Vacancy]):
        # обнуление всех scores
        for vacancy in vacancy_list:
            vacancy.bm25_score = 0.0
            vacancy.embedding_score = 0.0
            vacancy.llm_score = 0.0
            vacancy.total_score = 0.0

        skill_weights = {skill_item.skill: float(skill_item.level) for skill_item in
                         resume_analysis.skills_sorted_by_level}

        self.custom_bm25_scores(vacancy_list, skill_weights)
        self.embedding_scores(resume_analysis, vacancy_list)

        vacancy_list.sort(key=lambda v: v.total_score, reverse=True)

        self.llm_matching(resume_analysis, vacancy_list[
            :self.vacancy_cnt_for_llm_matching]
        )

        vacancy_list.sort(key=lambda v: v.total_score, reverse=True)

    @staticmethod
    def _normalize_scores(scores : list[float]) -> list[float]:
        max_score = max(scores)
        min_scores = min(scores)

        if max_score == min_scores:
            return [0.0 for _ in scores]

        return [(score - min_scores) / (max_score - min_scores) for score in scores]

    @staticmethod
    def _convert_vacancy_to_text(vacancy: Vacancy) -> str:
        return vacancy.description # временно

    @staticmethod
    def _convert_resume_to_text(resume: ResumeAnalysis) -> str:
        hh_filter = HHFilters("hh/hh_filters.json")

        # Собираем только значимые факты
        chunks = [
            f"Профессия: {resume.profession_name}.",
            f"Опыт работы: {hh_filter.get_dictionaries_name(resume.experience)}."
        ]

        # Ключевые навыки
        skills_list = [skill_item.skill
                       for skill_item in resume.skills_sorted_by_level
        ]

        if skills_list:
            chunks.append(f"Навыки: {', '.join(skills_list)}.")

        chunks.append(f"Описание: {resume.brief_description.strip()}")

        # Иностранные языки
        lang_list = [f"{lang_item.language} {lang_item.level}"
                     for lang_item in resume.languages_with_level
        ]

        if lang_list:
            chunks.append(f"Языки: {', '.join(lang_list)}.")

        # Условия работы (объединяем в один смысловой блок)
        formats = [hh_filter.get_dictionaries_name(f) for f in resume.work_formats if f]
        schedules = [hh_filter.get_dictionaries_name(s) for s in resume.work_schedule_by_days if s]
        hours = [hh_filter.get_dictionaries_name(h) for h in resume.working_hours if h]

        conditions = []
        if formats:
            conditions.append(f"формат: {', '.join(formats)}")
        if schedules:
            conditions.append(f"график: {', '.join(schedules)}")
        if hours:
            conditions.append(f"занятость: {', '.join(hours)}")

        if conditions:
            chunks.append(f"Условия работы: {'; '.join(conditions)}.")

        # Объединяем всё через один пробел в единый текстовый корпус
        return " ".join(chunks)

    @staticmethod
    def _skill_weights_prepare(skill_w : dict[str, float]):
        skill_weights_lower = {skill.lower() : weight for skill, weight in skill_w.items()}
        return skill_weights_lower

    @staticmethod
    def _vacancy_texts_prepare(vacancy_texts : list[str]) -> list[list[str]]:
        tokenized_vacancy_texts = []

        for vacancy_text in vacancy_texts:
            text = vacancy_text.lower()

            pattern = r'[a-zа-я0-9\._]+(?:[\+#]+)?'
            tokens = re.findall(pattern, text)
            cleaned_tokens = [token.rstrip(".") for token in tokens]

            tokenized_vacancy_texts.append(cleaned_tokens)

        return tokenized_vacancy_texts


if __name__ == "__main__":
    pass
