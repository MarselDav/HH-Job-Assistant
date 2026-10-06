SELECT
    hh_id,
    name,
    company_id,
    area,
    experience,
    response_letter_required,
    salary,
    salary_mode,
    currency_code,
    work_formats,
    work_schedule_by_days,
    working_hours,
    description
FROM vacancies
WHERE hh_id = %s;