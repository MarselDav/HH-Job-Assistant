import html
import json
import re
import requests


URL = "https://hh.ru/search/vacancy"

params = {
    "text": "C++ Qt",
}

headers = {
    "User-Agent": "Mozilla/5.0"
}



# """
# https://hh.ru/search/vacancy?resume=55d52a0eff0e784c8f0039ed1f4d6175663578&utm_source=email&utm_medium=email&utm_campaign=vacancies_selected&utm_content=butt_all&sent_date=2026_09_03&email_hash=b43b6dffb21495e29ee8973c5093eacc&search_field=name&search_field=company_name&search_field=description&work_format=ON_SITE&enable_snippets=true&hhtmSource=vacancy_search_list&hhtmSourceLabel=vacancy_search_list&hhtmFrom=vacancy_search_list&hhtmFromLabel=drawer_filter&experience=noExperience
# """


response = requests.get(
    URL,
    params=params,
    headers=headers,
    timeout=30,
)

print(response.url)

response.raise_for_status()

page = response.text


pattern = re.compile(
    r'<template[^>]*id="HH-Lux-InitialState"[^>]*>(.*?)</template>',
    re.DOTALL,
)

match = pattern.search(page)

if not match:
    print("HH-Lux-InitialState not found")
    exit(1)


raw_json = match.group(1)

decoded_json = html.unescape(raw_json)

data = json.loads(decoded_json)


print("JSON successfully parsed!")
print("Top-level keys:")
print(*data.keys(), sep="\n- ")


vacancies = data["vacancySearchResult"]["vacancies"]

print("Vacancies:", len(vacancies))
#
# for vacancy in vacancies:
#     print(vacancy)


print(vacancies[0])