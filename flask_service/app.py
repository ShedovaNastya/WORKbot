from flask import Flask, request, jsonify
import requests
import psycopg2
import os

app = Flask(__name__)

# Устанавливаем соединение с базой данных PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL is None:
    conn = psycopg2.connect(database='work', user='postgres', password='95299392', host='localhost', port='5432')
else:
    conn = psycopg2.connect(DATABASE_URL)
# Создаем объект курсора для выполнения SQL-запросов
cursor = conn.cursor()
# Включаем автоматический коммит для соединения, чтобы каждый запрос автоматически фиксировался в базе данных
conn.autocommit = True

create_salary_tab_query = """
CREATE TABLE IF NOT EXISTS salary_tab (
    id_salary SERIAL PRIMARY KEY, 
    salary_from INT,
    salary_to INT,
    currency TEXT,
    UNIQUE (salary_from, salary_to, currency)
);
"""

create_vacancies_query = """
CREATE TABLE IF NOT EXISTS vacancies (
    id_vac SERIAL PRIMARY KEY,
    title_vacancy TEXT NOT NULL,
    region TEXT NOT NULL,
    salary INT NOT NULL REFERENCES salary_tab(id_salary),
    experience TEXT,
    employment TEXT,
    url VARCHAR(255) NOT NULL,
    UNIQUE (title_vacancy, region, salary, experience, employment, url)
);
"""

def create_tables(conn):

    # Устанавливаем соединение и курсор
    cursor = conn.cursor()

    # Проверяем существование таблиц
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'salary_tab')")
    salary_tab_exists = cursor.fetchone()[0]

    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'vacancies')")
    vacancies_exists = cursor.fetchone()[0]

    # Создаем таблицы, если они не существуют
    if not salary_tab_exists:
        cursor.execute(create_salary_tab_query)
        print("Таблица salary_tab создана")

    if not vacancies_exists:
        cursor.execute(create_vacancies_query)
        print("Таблица vacancies создана")

create_tables(conn)

exp_dict = {
    "noExperience": "Нет опыта",
    "between1And3": "От 1 года до 3 лет",
    "between3And6": "От 3 до 6 лет",
    "moreThan6": "Более 6 лет"
}

emp_dict = {"full": "Полная занятость",
            "part": "Частичная занятость",
            "project": "Проектная работа",
            "volunteer": "Волонтерство",
            "probation": "Стажировка"
}

headers = {
    "User-Agent": "api-test-agent",
    "Content-Type": "application/json"
}

def inserter(files):
    items = files['items']
    # print(items)

    insert_salary_query = """
                        INSERT INTO salary_tab (salary_from, salary_to, currency)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (salary_from, salary_to, currency) DO NOTHING
                        RETURNING id_salary;
                        """

    insert_vacancy_query = """
                        INSERT INTO vacancies (title_vacancy, region, salary, experience, employment, url)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (title_vacancy, region, salary, experience, employment, url) DO NOTHING;
                        """

    for i in range(len(items)):
        if items[i]['salary']:
            salary_data = {
                'salary_from': items[i]['salary']['from'],
                'salary_to': items[i]['salary']['to'],
                'currency': items[i]['salary']['currency']
            }
        else:
            salary_data = {
                'salary_from': None,
                'salary_to': None,
                'currency': None
            }

        cursor.execute(insert_salary_query, (salary_data['salary_from'], salary_data['salary_to'], salary_data['currency']))

        id_salary = cursor.fetchone()

        if not id_salary:
            select_salary_query = """
            SELECT id_salary FROM salary_tab
            WHERE salary_from = %s AND salary_to = %s AND currency = %s;
            """
            cursor.execute(select_salary_query, (salary_data['salary_from'], salary_data['salary_to'], salary_data['currency']))
            id_salary = cursor.fetchone()[0]
        else:
            id_salary = id_salary[0]

        if items[i]['name'] is None:
            continue
        if items[i]['area'] is None:
            items[i]['area']['name'] = None
        if items[i]['experience'] is None:
            items[i]['experience']['name'] = None
        if items[i]['employment'] is None:
            items[i]['employment']['name'] = None
        if items[i]['alternate_url'] is None:
            continue

        vacancy_data = {
            'title_vacancy': items[i]['name'],
            'region': items[i]['area']['name'],
            'experience': items[i]['experience']['name'],
            'employment': items[i]['employment']['name'],
            'url': items[i]['alternate_url']
        }
        cursor.execute(insert_vacancy_query, (
            vacancy_data['title_vacancy'],
            vacancy_data['region'],
            id_salary,
            vacancy_data['experience'],
            vacancy_data['employment'],
            vacancy_data['url']
        ))
        conn.commit()




def get_vacancies(vacancy_name, params, search_field="name"):
    url = "https://api.hh.ru/vacancies"
    params['text'] = vacancy_name
    response = requests.get(url, headers=headers, params=params)

    
    if response.status_code == 200:
        data = response.json()
        inserter(data)
        vacancies = data.get('items', [])[:]
        selected_keys = ['name', 'area', 'salary', 'experience', 'employment', 'alternate_url']
        result = [{key: vacancy.get(key) for key in selected_keys if key in vacancy} for vacancy in vacancies]
        # print(result)
        # print(data)
        try:
            temp = result[0]
        except:
            result = []
        return jsonify(result)
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
    """
    todo:
        - search with filters
    """
    vacancy_name = request.args.get('vacancy_name')
    exp = request.args.get('experience')
    reg = request.args.get("region")
    emp = request.args.get("employment")
    postfix = ""
    if exp:
        postfix += f" and experience='{exp_dict[exp]}'"
    if reg:
        postfix += f" and region='{reg}'"
    if emp:
        postfix += f" and employment='{emp_dict[emp]}'"
    
    if not vacancy_name:
        return jsonify({"error": "Missing vacancy_name parameter"}), 400

    cnt_loc = "SELECT count(*) FROM vacancies join salary_tab ON (id_vac = id_salary) where title_vacancy ILIKE %s" + postfix
    cursor.execute(cnt_loc, (f"%{vacancy_name}%",))
    result_cnt = cursor.fetchall()
 
    return result_cnt

@app.route('/get_vacancies_bd', methods=['GET'])
def get_vacancies_bd():
    vacancy_name = request.args.get('vacancy_name')
    exp = request.args.get('experience')
    reg = request.args.get("region")
    emp = request.args.get("employment")
    postfix = ""
    if exp:
        postfix += f" and experience='{exp_dict[exp]}'"
    if reg:
        postfix += f" and region='{reg}'"
    if emp:
        postfix += f" and employment='{emp_dict[emp]}'"
    
    if not vacancy_name:
        return jsonify({"error": "Missing vacancy_name parameter"}), 400
    # мои записи из бд
    query = "SELECT * FROM vacancies join salary_tab ON (id_vac = id_salary) where title_vacancy ILIKE %s" + postfix
    cursor.execute(query, (f"%{vacancy_name}%", ))
    result_bd = cursor.fetchall()
    return result_bd

@app.route('/get_vacanices_api', methods=['GET'])
def get_vacancies_api():
    vacancy_name = request.args.get('vacancy_name')
    # search_field = request.args.get('search_field', 'name')
    params = {}
    params['search_field'] = 'name'
    experience = request.args.get("experience", "")
    if experience != "":
        params['experience'] = experience
    area = request.args.get("area", "")
    if area != "":
        params['area'] = area
    employment = request.args.get("employment", '')
    if employment != "":
        params['employment'] = employment

    return get_vacancies(vacancy_name=vacancy_name, params=params)


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
    app.run(host='0.0.0.0', port=5000, debug=True)