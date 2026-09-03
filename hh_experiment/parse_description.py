import requests


url = "https://hh.ru/vacancy/136289332"

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30,
)

response.raise_for_status()

print("Status:", response.status_code)
print("Size:", len(response.content))

with open(
    "vacancy.html",
    "wb",
) as file:
    file.write(response.content)