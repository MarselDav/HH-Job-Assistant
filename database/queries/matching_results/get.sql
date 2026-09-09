SELECT
    vacancy_id,
    bm25_score,
    embedding_score,
    llm_score,
    total_score,
    matched_skills,
    recap
FROM matching_results
WHERE vacancy_id = %s;