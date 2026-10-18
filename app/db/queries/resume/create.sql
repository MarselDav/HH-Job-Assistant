INSERT INTO resumes (
    name,
    raw_text
)
VALUES (
    %s, %s
)
RETURNING id;