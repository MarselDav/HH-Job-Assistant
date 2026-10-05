INSERT INTO companies (
    hh_id,
    name,
    description,
    logo,
    site_url
)
VALUES (
    %s, %s, %s, %s, %s
)
ON CONFLICT (hh_id) DO UPDATE
SET hh_id = EXCLUDED.hh_id -- EXCLUDED - виртуальная таблица, в которой данные которые не получилось вставить
RETURNING id;