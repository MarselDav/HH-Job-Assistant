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