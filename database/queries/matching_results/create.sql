INSERT INTO matching_results (
    vacancy_id,
    bm25_score,
    embedding_score,
    llm_score,
    total_score,
    matched_skills,
    recap
)
VALUE (
    %s, %s, %s, %s, %s, %s, %s
)
RETURNING id;