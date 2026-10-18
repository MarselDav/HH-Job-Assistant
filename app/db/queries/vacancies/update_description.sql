UPDATE vacancies
SET description = %s
WHERE id = %s
RETURNING id;