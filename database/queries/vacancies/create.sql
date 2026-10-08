INSERT INTO vacancies (
    hh_id,
    name,
    company_id,
    area,
    experience,
    response_letter_required,
    salary_from,
    salary_to,
    salary_mode,
    currency,
    work_formats,
    work_schedule_by_days,
    working_hours,
    description
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (hh_id) DO UPDATE
SET hh_id = EXCLUDED.hh_id -- EXCLUDED - виртуальная таблица, в которой данные которые не получилось вставить
RETURNING id;