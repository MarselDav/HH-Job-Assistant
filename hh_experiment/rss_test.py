import requests
import xml.etree.ElementTree as ET


URL = "https://hh.ru/search/vacancy/rss"

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

response.raise_for_status()

print("Status:", response.status_code)
print("URL:", response.url)
print()


root = ET.fromstring(response.content)

for item in root.findall(".//item"):
    title = item.findtext("title")
    link = item.findtext("link")
    pub_date = item.findtext("pubDate")

    print("Название:", title)
    print("Ссылка:", link)
    print("Дата:", pub_date)
    print("-" * 80)