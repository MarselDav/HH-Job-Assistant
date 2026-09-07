from hh_models import VacancySearchFilters, Area
from hh_vacancy_client import HHVacancyClient
from llm.resume_analyzer import ResumeAnalyzer
from llm.llm_client import LLMClient

from vacancy_retriever import VacancyRetriever
from sentence_transformers import SentenceTransformer

if __name__ == "__main__":
    vsf = VacancySearchFilters(
        text="C++",
        area=[Area("Москва", ""), Area("Санкт-Петербург", "")],
        experience=["Нет опыта"],
        work_format=["Удалённо"],
    )

    hh = HHVacancyClient("hh_filters.json")
    vac_list = hh.search(vsf)
    hh.load_descriptions(vac_list)

    with open("resume_example.txt", "r", encoding="utf-8") as f:
        resume_str = f.read()

    analyzer = ResumeAnalyzer(model=LLMClient())
    resume_analysis = analyzer.analyze(resume_str)

    embedding_model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    vr = VacancyRetriever(embedding_model)

    skill_weights = {skill_item.skill : float(skill_item.level) for skill_item in resume_analysis.skills_sorted_by_level}

    print(vr.custom_bm25_scores(vac_list, skill_weights))
    print(vr.embedding_scores(resume_analysis, vac_list))