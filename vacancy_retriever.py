from statistics import mean
from sentence_transformers import SentenceTransformer
from hh_filters import HHFilters
from hh_models import Vacancy
from llm.resume_analyzer import ResumeAnalysis
import re


class VacancyRetriever:
    def __init__(self, embedding_model : SentenceTransformer) -> None:
        self.embedding_model = embedding_model

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

        return final_scores_list


    def embedding_scores(self, resume : ResumeAnalysis, vacancies_list : list[Vacancy]) -> list[float]:
        resume_text = self._convert_resume_to_text(resume)
        vacancy_texts = [self._convert_vacancy_to_text(vacancy) for vacancy in vacancies_list]

        resume_embedding = self.embedding_model.encode_query(
            resume_text,
            convert_to_tensor=True
        )

        vacancy_embedding = self.embedding_model.encode_query(
            vacancy_texts,
            convert_to_tensor=True
        )

        similarities = self.embedding_model.similarity(
            resume_embedding,
            vacancy_embedding
        )

        return similarities[0].tolist()

    @staticmethod
    def _convert_vacancy_to_text(vacancy: Vacancy) -> str:
        return vacancy.description # временно

    @staticmethod
    def _convert_resume_to_text(resume: ResumeAnalysis) -> str:
        hh_filter = HHFilters("hh_filters.json")

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


from hh_models import VacancySearchFilters, Area
from hh_vacancy_client import HHVacancyClient

if __name__ == "__main__":
    vsf = VacancySearchFilters(
        text="C++",
        area=[Area("Москва", ""), Area("Санкт-Петербург", "")],
        experience=["Нет опыта"],
        work_format=["Удалённо"],
    )

    hh = HHVacancyClient("hh_filters.json")
    vac_list = hh.search(vsf)

    vac_list_part = vac_list[:5:]
    hh.load_descriptions(vac_list_part)

    for vacancy in vac_list_part:
        print("-" * 10)
        print(vacancy.description)

    skill_weights = {
        "c++" : 1.0,
        "python" : 0.8,
    }

    embedding_model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    vr = VacancyRetriever(embedding_model)
    bm25_scores = vr.custom_bm25_scores(
        [vacancy.description for vacancy in vac_list_part], skill_weights
    )

    embedding_scores = vr.embedding_scores()
