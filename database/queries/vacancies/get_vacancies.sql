SELECT
    id AS db_id,
    hh_id AS id,
    name,
    work_schedule,
    response_letter_required,
    company_id,
    company_name,
    area,
    experience,
    salary,
    work_formats,
    work_schedule_by_days,
    working_hours,
    description
FROM vacancies
WHERE id = ANY(%s);