UPDATE resumes
SET analysis = %s
WHERE id = %s
RETURNING id;