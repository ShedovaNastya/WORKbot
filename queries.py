import requests

headers = {
    "User-Agent": "api-test-agent",
    "Content-Type": "application/json"}

def get_vacancies(vacancy_name, search_field="name"):
    params = {
        "text": vacancy_name,
        'search_field': search_field
    }
    url = "https://api.hh.ru/vacancies"
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        vacancies = data.get('items', [])[:]
        selected_keys = ['name', 'area', 'salary', 'experience', 'employment','alternate_url']
        result = [{key: vacancy.get(key) for key in selected_keys if key in vacancy} for vacancy in vacancies]
        return result
    elif response.status_code == 400:
        return "Ошибка 400: Параметры переданы с ошибкой"
    elif response.status_code == 403:
        return '"Ошибка 403: Требуется ввести капчу"'
    elif response.status_code == 404:
        return "Ошибка 404: Указанная вакансия не существует"
    else:
        return 'Неизвестная ошибка'


def distionaries(key_field):
    url = "https://api.hh.ru/dictionaries"
    response = requests.get(url, headers=headers)
    return response.json()[key_field]







