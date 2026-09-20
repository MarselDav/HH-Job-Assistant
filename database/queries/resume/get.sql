SELECT
	name,
	raw_text,
	analysis,
	created_at
FROM resumes
WHERE id = %s;