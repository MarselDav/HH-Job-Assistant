import requests


URL = "https://hh.ru/search/vacancy"

params = {
    "text": "C++ Qt",
    "experience": "noExperience",
}

"""
https://hh.ru/search/vacancy?resume=55d52a0eff0e784c8f0039ed1f4d6175663578&utm_source=email&utm_medium=email&utm_campaign=vacancies_selected&utm_content=butt_all&sent_date=2026_09_03&email_hash=b43b6dffb21495e29ee8973c5093eacc&search_field=name&search_field=company_name&search_field=description&work_format=ON_SITE&work_format=REMOTE&work_format=HYBRID&enable_snippets=true&hhtmSource=vacancy_search_list&hhtmSourceLabel=vacancy_search_list&hhtmFrom=vacancy_search_list&hhtmFromLabel=drawer_filter&text=C%2B%2B+%2C+qt&area=1&experience=noExperience&experience=between1And3&working_hours=HOURS_8&work_schedule_by_days=FIVE_ON_TWO_OFF

"""

headers = {
    "User-Agent": "Mozilla/5.0"
}


response = requests.get(
    URL,
    params=params,
    headers=headers,
    timeout=30,
)

response.raise_for_status()


print("Status:", response.status_code)
print("URL:", response.url)
print("Content-Type:", response.headers.get("Content-Type"))
print("Size:", len(response.content), "bytes")

with open("hh_search.html", "wb") as file:
    file.write(response.content)

print("HTML saved to hh_search.html")