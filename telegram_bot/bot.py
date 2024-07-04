import telebot
from telebot import types
import requests
import json
import os


token = os.getenv("TELEGRAM_TOKEN")
if token is None:
    token = ##############################################
number_of_output_vacancies = 5

flask_url = os.getenv("FLASK_URL")
if flask_url is None:
    flask_url = "http://127.0.0.1:5000"

bot = telebot.TeleBot(token)

class user_states:
    _user_states = {} # состояние пользователя
    
    @classmethod
    def get(cls, key):
        return cls._user_states[key]
    
    @classmethod
    def set(cls, key, value):
        cls._user_states[key] = value


class vacancies_from_bd:
    _array = []

    @classmethod
    def set_array(cls, new_array):
        cls._array = new_array

    @classmethod
    def len(cls):
        return len(cls._array)
    
    @classmethod
    def slice(cls, st=0, end=-1):
        return cls._array[st:end]
    
    @classmethod
    def repr(cls):
        return repr(cls._array)
    
    @classmethod
    def all(cls):
        return cls._array


class vacancies_counter:
    """
    singletone переменная для подсчета количества выведенных вакансий
    """
    value = 0

class count_vacancies_all:
    """
    singletone переменная для подсчета всех вакансий, найденных в бд
    """
    value = 0

class current_vacancy:
    value = ""

class filter_vacancy:
    exp = ""
    region = ""
    emp = ""

    def reset(cls):
        cls.exp = ""
        cls.region = ""
        cls.emp = ""

def create_query(vacancy):
    params = {
        'vacancy_name': vacancy
    }
    if filter_vacancy.exp != "":
        params['experience'] = filter_vacancy.exp
    if filter_vacancy.region != "":
        params["area"] = filter_vacancy.region
    if filter_vacancy.emp != "":
        params["employment"] = filter_vacancy.emp
    return params

def check_salary(data):
    if data is None:
        return "О зарплате нет данных"
    for key, value in data.items():
        if key == 'to' and value != None:
            return(f'до {data[key]} RUR')
    return 'Размер зарплаты обсуждается лично'

def vacancies_to_string(vacancies):
    """
    Преобразует список вакансий в строку, где каждая вакансия представлена в виде строки,
    содержащей значения её полей, разделенных символом новой строки"""
    result = [vacancies['name'],vacancies['area'],  vacancies['salary'],  vacancies['experience'],vacancies['employment'],  vacancies['alternate_url']]

    return result
    
@bot.message_handler(commands=['us'])
def us(message): 
    # dev function
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/start")
    markup.add(item1)
    bot.send_message(message.chat.id, f'{user_states.get(message.chat.id)}', reply_markup=markup)
    # user_states.set(message.chat.id, 'ввод_вакансии') # переход на страницу поиска вакансий

@bot.message_handler(commands=['flt'])
def us(message): 
    # dev function
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/start")
    markup.add(item1)
    bot.send_message(message.chat.id, f'{filter_vacancy.emp}, {filter_vacancy.exp}, {filter_vacancy.region}', reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message): 
    # initializer()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Ввести вакансию")
    markup.add(item1)
    bot.send_message(message.chat.id, 'Привет, тебя приветствует 💻WORKbot💻 Самый простой и удобный способ найти для себя лучшую вакансию.'
                     'Скорее жми на кнопку "Искать вакансию"👨‍💼🙈👩‍💼', reply_markup=markup)
    user_states.set(message.chat.id, 'ввод_вакансии') # переход на страницу поиска вакансий


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'ввод_вакансии')
def answer(message):
    user_text = message.text
    if user_text == "Ввести вакансию":
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Напишите название вакансии, которая вас интересует",reply_markup=markup)
        user_states.set(message.chat.id,'выбор_дальнейший_действий')
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Ввести вакансию")
        markup.add(item1)
        bot.send_message(message.chat.id, "нажмите кнопку", reply_markup=markup)
        user_states.set(message.chat.id,'ввод_вакансии',)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "выбор_дальнейший_действий")
def select(message):
    if message.text != "Вернуться к выбору действий":
        current_vacancy.value = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Локальный поиск")
    item2 = types.KeyboardButton("Поиск по апи")
    item3 = types.KeyboardButton("Настройка фильтра")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Выберите дальнейшие действия", reply_markup=markup)
    user_states.set(message.chat.id, "выбор_дальнейший_действий_обработка_кнопок")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "выбор_дальнейший_действий_обработка_кнопок")
def button_handler_bd_api_filter(message):
    user_text = message.text
    if user_text == "Локальный поиск":
        user_states.set(message.chat.id, "запрос_в_бд")
        db_query(message)
    elif user_text == "Поиск по апи":
        user_states.set(message.chat.id, "запрос_по_апи")
        api_query(message)
    elif user_text == "Настройка фильтра":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter(message)
    else:
        bot.send_message(message.chat.id, "нажмите одну из кнопок")
        user_states.set(message.chat.id, "выбор_дальнейший_действий_обработка_кнопок")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "запрос_в_бд")
def db_query(message):
    print(user_states.get(message.chat.id))
    url = f"{flask_url}/get_count_vacancies_bd"

    # Параметры запроса
    params = create_query(current_vacancy.value)

    # Выполнение GET запроса
    response = requests.get(url, params=params)

   
    if response.status_code == 200:
        print(response.json())
        vacancies_count = response.json()[0][0]
        if vacancies_count==0:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Искать по апи")
            item2 = types.KeyboardButton("Изменить фильтр")
            item3 = types.KeyboardButton("Ввести вакансию")
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, "вакансий не найдено, попробуйте искать по апи, изменить фильтр или вакансию", reply_markup=markup)
            user_states.set(message.chat.id,'апи_фильтр_вакансия')
            button_handler_api_filter_vacancy(message)
            return
        else:
            count_vacancies_all.value = vacancies_count
            vacancies_counter.value = 0
            bot.send_message(message.chat.id, f'Локально найдено {vacancies_count} вакансий')
            user_states.set(message.chat.id, "вывод_вакансий_из_бд")
            send_vacancies_from_bd(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("/start")
        markup.add(item1)
        bot.send_message(message.chat.id, "возникла непредвиденная ошибка, попробуйте перезапустить бота, нажав на кнопку", reply_markup=markup)
        return
    
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "апи_фильтр_вакансия")
def button_handler_api_filter_vacancy(message):
    user_text = message.text
    if user_text == "Искать по апи":
        user_states.set(message.chat.id, "запрос_по_апи")
        # print('api')
        api_query(message)
    elif user_text == "Изменить фильтр":
        user_states.set(message.chat.id, "настройка_фильтра")
        # print('filter')
        filter(message)
    elif user_text == "Ввести вакансию":
        user_states.set(message.chat.id, "ввод_вакансии")
        # print('vacanci')
        answer(message)
    elif user_text=="Локальный поиск":
        user_states.set(message.chat.id, "апи_фильтр_вакансия")
    else:
        bot.send_message(message.chat.id, "ннажмите одну из кнопок")
        user_states.set(message.chat.id, "апи_фильтр_вакансия")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "вывод_вакансий_из_бд")
def send_vacancies_from_bd(message):
    flag = 0
    if vacancies_counter.value == 0:
        url = f"{flask_url}/get_vacancies_bd"

        # Параметры запроса
        params = create_query(current_vacancy.value)

        # Выполнение GET запроса
        response = requests.get(url, params=params)
        vacancies_from_bd.set_array(response.json())
        print(vacancies_from_bd.all())
        # print(vacancies_from_bd._array)

    if vacancies_from_bd.len() > number_of_output_vacancies:
        output = vacancies_from_bd.slice(0, number_of_output_vacancies)
        vacancies_from_bd.set_array(vacancies_from_bd.slice(number_of_output_vacancies, vacancies_from_bd.len()))
        count_vacancies_all.value -= number_of_output_vacancies
    else:
        output = vacancies_from_bd._array
        vacancies_from_bd.set_array([])
        count_vacancies_all.value = 0
        flag = 1

    for cnt in range(len(output)):
        ans = ''
        for i in range(1,10):
            if i == 2 :
                ans += 'Город: ' + str((output[cnt][i])) + '   '
            if i == 1:
                ans += f"Вакансия № {vacancies_counter.value+1}: " + str((output[cnt][i])) + '   '
            if i == 3:
                continue
            if i == 4:
                ans += "Опыт работы:  " + str((output[cnt][i])) + '   '
            if i == 5:
                ans += "Занятость: "+ str((output[cnt][i])) + '   '
            if i == 8 or i == 9:
                if i == 8:
                    ans += "Зарплата от "+ str((output[cnt][i])) + ' '
                else:
                    ans += " до "+ str((output[cnt][i])) + '   '
        ans += "Ссылка на объявление: "+ str((output[cnt][6])) + '   '
        split_ans = ans.split("   ")
        new_line_ans = '\n'.join(split_ans)
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, str(new_line_ans), reply_markup=markup)
        vacancies_counter.value += 1

    if flag == 0:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Вывести ещё")
        item2 = types.KeyboardButton("Изменить фильтр")
        item3 = types.KeyboardButton("Изменить вакансию")
        item4 = types.KeyboardButton("Искать по апи")
        markup.add(item1, item2, item3, item4)
        bot.send_message(message.chat.id, "Выберите дальнейшее действие", reply_markup=markup)
        user_states.set(message.chat.id, "ещё_фильтр_вакансия_апи")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Искать по апи")
        item2 = types.KeyboardButton("Изменить фильтр")
        item3 = types.KeyboardButton("Ввести вакансию")
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id, "вакансий больше, попробуйте искать по апи, изменить фильтр или вакансию", reply_markup=markup)
        user_states.set(message.chat.id,'апи_фильтр_вакансия')
        button_handler_api_filter_vacancy(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "ещё_фильтр_вакансия_апи")
def button_handler_other_filter_vacancy_api(message):
    if message.text == "Вывести ещё":
        user_states.set(message.chat.id, "вывод_вакансий_из_бд")
        send_vacancies_from_bd(message)
    elif message.text == "Изменить фильтр":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter(message)
    elif message.text == "Изменить вакансию":
        user_states.set(message.chat.id, "ввод_вакансии")
        answer(message)
    elif message.text == "Искать по апи":
        user_states.set(message.chat.id, "запрос_по_апи")
        api_query(message)
    else:
        user_states.set(message.chat.id, "ещё_фильтр_вакансия_апи")
        bot.send_message(message.chat.id, "нажмите корректную кнопку")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "запрос_по_апи")
def api_query(message):
    url = f"{flask_url}/get_vacanices_api"

    # Параметры запроса
    params = create_query(current_vacancy.value)
    if 'area' in params.keys():
        if params['area'] != "":
            with open('city2id.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                params['area'] = data[params['area']]
    # Выполнение GET запроса
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        print(response)
        number_of_founded_vacancies = len(response.json())
        if number_of_founded_vacancies == 0:
            markup = types.ReplyKeyboardMarkup()
            item1 = types.KeyboardButton("Изменить фильтр")
            item2 = types.KeyboardButton("Ввести вакансию")
            item3 = types.KeyboardButton("Обратиться локально")
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, "Вакансий по данном запросу не найдено. Попробуйте изменить фильтр, ввести вакансию или обратиться локально", reply_markup=markup)
            user_states.set(message.chat.id, "фильтр_вакасня_бд")
            # button_handler_filter_vacancy_bd(message)
        else:
            for i in range(20):
                post_preprocess_vacancies = vacancies_to_string(response.json()[i])
                # print(post_preprocess_vacancies)
                post_preprocess_vacancies[1] = post_preprocess_vacancies[1]['name']
                post_preprocess_vacancies[2] = check_salary(post_preprocess_vacancies[2])
                
                post_preprocess_vacancies[3] = post_preprocess_vacancies[3]['name']
                post_preprocess_vacancies[4] = post_preprocess_vacancies[4]['name']
                vacancies_str = '\n'.join(post_preprocess_vacancies)
                markup = types.ReplyKeyboardRemove(selective=False)
                bot.send_message(message.chat.id, vacancies_str, reply_markup=markup)

            markup = types.ReplyKeyboardMarkup()
            item1 = types.KeyboardButton("Изменить фильтр")
            item2 = types.KeyboardButton("Ввести вакансию")
            item3 = types.KeyboardButton("Обратиться локально")
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, "Больше вакансий получить не предоставалется возможным в связи с жадносью охотников за головами. Выберите дальнейшие действия", reply_markup=markup)
            user_states.set(message.chat.id, "фильтр_вакасня_бд")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("/start")
        markup.add(item1)
        bot.send_message(message.chat.id, "возникла непредвиденная ошибка, попробуйте перезапустить бота, нажав на кнопку", reply_markup=markup)
        return
    
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "фильтр_вакасня_бд")
def button_handler_filter_vacancy_bd(message):
    if message.text == "Изменить фильтр":
        user_states.set(message.chat.id, "настройка_фильтра")
        filter(message)
    elif message.text == "Ввести вакансию":
        user_states.set(message.chat.id, "ввод_вакансии")
        answer(message)
    elif message.text == "Обратиться локально":
        user_states.set(message.chat.id, "запрос_в_бд")
        db_query(message)
    else:
        bot.send_message(message.chat.id, "нажмите одну из кнопок")
        user_states.set(message.chat.id, "фильтр_вакасня_бд")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "настройк_фильтра")
def filter(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Выбор занятости")
    item2 = types.KeyboardButton("Выбор региона")
    item3 = types.KeyboardButton("Выбор опыта")
    item4 = types.KeyboardButton("Вернуться к выбору действий")
    item5 = types.KeyboardButton("Cброс фильтра")
    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(message.chat.id, "Выберите, какую настройку вы хотите изменить", reply_markup=markup)
    user_states.set(message.chat.id, "занятость_регион_опыт_выбор_дальнейших действий")
    button_handler_employment_region_experience_select(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "занятость_регион_опыт_выбор_дальнейших")
def button_handler_employment_region_experience_select(message):
    if message.text == "Выбор опыта":
        user_states.set(message.chat.id, "фильтр_опыт")
        filter_experiance(message)
    elif message.text == "Выбор региона":
        user_states.set(message.chat.id, "фильтр_регион")
        filter_region(message)
    elif message.text == "Выбор занятости":
        user_states.set(message.chat.id, "фильтер_занятость")
        filter_employment(message)
    elif message.text == "Вернуться к выбору действий":
        user_states.set(message.chat.id, "выбор_дальнейший_действий")
        select(message)
    elif message.text == "Cброс фильтра":##########################################################33
        # print("сброс")
        filter_vacancy.emp =""
        filter_vacancy.exp = ""
        filter_vacancy.region = ""
        user_states.set(message.chat.id, "занятость_регион_опыт_выбор_дальнейших")
    else:
        user_states.set(message.chat.id, "занятость_регион_опыт_выбор_дальнейших")
        bot.send_message(message.chat.id, "нажмите одну из кнопок")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "фильтр_опыт")
def filter_experiance(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Нет опыта")
    item2 = types.KeyboardButton("От 1 года до 3 лет")
    item3 = types.KeyboardButton("От 3 до 6 лет")
    item4 = types.KeyboardButton("Более 6 лет")
    item5 = types.KeyboardButton("Ничего не менять")
    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(message.chat.id, "Выберите одну из предложенных опций", reply_markup=markup)
    user_states.set(message.chat.id, "Выбор_опыт")
    select_experiance(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "Выбор_опыт")
def select_experiance(message):
    print('adfs')
    if message.text == "Нет опыта":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter_vacancy.exp = "noExperience"
        filter(message)
    elif message.text == "От 1 года до 3 лет":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter_vacancy.exp = "between1And3"
        filter(message)
    elif message.text == "От 3 до 6 лет":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter_vacancy.exp = "between3And6"
        filter(message)
    elif message.text == "Более 6 лет":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter_vacancy.exp = "moreThan6"
        filter(message)
    elif message.text == "Ничего не менять":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter(message)
    else:
        user_states.set(message.chat.id, "Выбор_опыт")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "фильтр_регион")
def filter_region(message):
    markup = types.ReplyKeyboardRemove(selective=True)
    bot.send_message(message.chat.id, "Введите город. Если хотите отказаться от выбора города, напишите 'нет'", reply_markup=markup)
    user_states.set(message.chat.id, "Выбор_города")
    select_region(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "Выбор_города")
def select_region(message):
    with open('city2id.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        if message.text.lower().capitalize() in data.keys():
            filter_vacancy.region = message.text.lower().capitalize()
            user_states.set(message.chat.id, "настройк_фильтра")
            filter(message)
        elif message.text.lower() == 'нет':
            user_states.set(message.chat.id, "настройк_фильтра")
            filter(message)
        else:
            bot.send_message(message.chat.id, "такой город не найден")
            user_states.set(message.chat.id, "Выбор_города")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "фильтер_занятость")
def filter_employment(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Полная занятость")
    item2 = types.KeyboardButton("Частичная занятость")
    item3 = types.KeyboardButton("Проектная работа")
    item4 = types.KeyboardButton("Волонтёрство")
    item5 = types.KeyboardButton("Стажировка")
    item6 = types.KeyboardButton("Ничего не менять")
    markup.add(item1, item2, item3, item4, item5, item6)
    bot.send_message(message.chat.id, "Выберите одну из предложенных опций", reply_markup=markup)
    user_states.set(message.chat.id, "Выбор_знаятости")
    select_employment(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "Выбор_знаятости")
def select_employment(message):
    if message.text == "Полная занятость":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter_vacancy.emp = "full"
        filter(message)
    elif message.text == "Частичная занятость":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter_vacancy.emp = "part"
        filter(message)
    elif message.text == "Проектная работа":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter_vacancy.emp = "project"
        filter(message)
    elif message.text == "Волонтёрство":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter_vacancy.emp = "volunteer"
        filter(message)
    elif message.text == "Стажировка":
        filter_vacancy.emp = "probation"
        user_states.set(message.chat.id, "настройк_фильтра")
        filter(message)
    elif message.text == "Ничего не менять":
        user_states.set(message.chat.id, "настройк_фильтра")
        filter(message)
    else:
        user_states.set(message.chat.id, "Выбор_знаятости")



bot.polling()  
    
