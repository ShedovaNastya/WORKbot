from flask import Flask, request, jsonify
import requests
import psycopg2
import sys

app = Flask(__name__)

# Устанавливаем соединение с базой данных PostgreSQL
conn = psycopg2.connect(database='work', user='postgres', password='95299392', host='localhost', port='5432')
# Создаем объект курсора для выполнения SQL-запросов
cursor = conn.cursor()
# Включаем автоматический коммит для соединения, чтобы каждый запрос автоматически фиксировался в базе данных
conn.autocommit = True

headers = {
    "User-Agent": "api-test-agent",
    "Content-Type": "application/json"
}

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
        selected_keys = ['name', 'area', 'salary', 'experience', 'employment', 'alternate_url']
        result = [{key: vacancy.get(key) for key in selected_keys if key in vacancy} for vacancy in vacancies]
        return result
    elif response.status_code == 400:
        return "Ошибка 400: Параметры переданы с ошибкой"
    elif response.status_code == 403:
        return "Ошибка 403: Требуется ввести капчу"
    elif response.status_code == 404:
        return "Ошибка 404: Указанная вакансия не существует"
    else:
        return 'Неизвестная ошибка'

@app.route('/get_count_vacancies_bd', methods=['GET'])
def get_count_vacancies_bd():
    vacancy_name = request.args.get('vacancy_name')
    search_field = request.args.get('search_field', 'name')
    
    if not vacancy_name:
        return jsonify({"error": "Missing vacancy_name parameter"}), 400

    cnt_loc = f"SELECT count(*) FROM vacancies join salary_tab ON (id_vac = id_salary) where title_vacancy = '{vacancy_name}'"
    cursor.execute(cnt_loc, (vacancy_name,))
    result_cnt = cursor.fetchall()
 
    return result_cnt

@app.route('/get_vacancies_bd', methods=['GET'])
def get_vacancies_bd():
    vacancy_name = request.args.get('vacancy_name')
    search_field = request.args.get('search_field', 'name')
    
    if not vacancy_name:
        return jsonify({"error": "Missing vacancy_name parameter"}), 400
    # мои записи из бд
    query = f"SELECT * FROM vacancies join salary_tab ON (id_vac = id_salary) where title_vacancy = '{vacancy_name}'"
    cursor.execute(query, (vacancy_name,))
    result_bd = cursor.fetchall()
    return result_bd

def distionaries(key_field):
    url = "https://api.hh.ru/dictionaries"
    response = requests.get(url, headers=headers)
    return response.json()[key_field]

@app.route('/get_dictionaries', methods=['GET'])
def get_dictionaries_route():
    key_field = request.args.get('key_field')
    
    if not key_field:
        return jsonify({"error": "Missing key_field parameter"}), 400
    
    result = distionaries(key_field)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)