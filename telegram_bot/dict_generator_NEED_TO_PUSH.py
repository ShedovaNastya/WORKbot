import requests
import re
import json
url = "https://api.hh.ru/areas"

# Параметры запроса
params = {'vacancy_name': "программист"}

headers = {
    "User-Agent": "api-test-agent",
    "Content-Type": "application/json"
}
# Выполнение GET запроса
response = requests.get(url, params=params, headers=headers)

pattern = re.compile(r"'id': '(\d+)',.*?'name': '([^']+)'")
res = pattern.findall(str(response.json()))
result1 = {i[0]:i[1] for i in res}
result2 = {i[1]:i[0] for i in res}
print(result1)
with open("id2city.json", 'w', encoding='utf-8') as file:
    json.dump(result1, file)
with open("city2id.json", 'w',encoding='utf-8') as file:
    json.dump(result2, file)
# print(str(response.json()))