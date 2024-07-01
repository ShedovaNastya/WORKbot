import telebot
from telebot import types
import psycopg2
import requests


token = "7418667479:AAHCK0hHCnzZ3pVAz9d-HRE1UvpRLoIQVuA"

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Искать вакансию")
    markup.add(item1)
    bot.send_message(message.chat.id, 'Привет, тебя приветствует 💻WORKbot💻Самый простой и удобный способ найти для себя лучшую вакансию. Скорее жми на кнопку "Искать вакансию"👨‍💼🙈👩‍💼', reply_markup=markup)

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

@bot.message_handler(content_types=['text'])
def answer(message):
    user_text = message.text
    url = "http://127.0.0.1:5000/get_vacancies"

    # Параметры запроса
    params = {
        'vacancy_name': user_text,
        'search_field': 'name'  # Опционально, если вы хотите изменить поле поиска
    }

    # Выполнение GET запроса
    response = requests.get(url, params=params)
   
    if response.status_code == 200:
        vacancies = response.json()
    else:
        print(f"Ошибка: {response.status_code}")
    
    if user_text == 'Искать вакансию':
        bot.send_message(message.chat.id, "Напишите название вакансии, которая вас интересует")
    elif len(vacancies) == 0 :
        bot.send_message(message.chat.id, "Вакансий по таком запросу нет")
    else:
        flag = 0
        ans = ''
        for i in range(1,10):
            if i == 2 :
                ans += 'Город: ' + str((vacancies[0][i])) + '   '
            if i == 1:
                ans += "Вакансия: " + str((vacancies[0][i])) + '   '
            if i == 3:
                continue
            if i == 4:
                ans += "Опыт работы:  " + str((vacancies[0][i])) + '   '
            if i == 5:
                ans += "Занятость: "+ str((vacancies[0][i])) + '   '
            if i == 8 or i == 9:
                if i == 8:
                    ans += "Зарплата от "+ str((vacancies[0][i])) + ' '
                else:
                    ans += " до "+ str((vacancies[0][i])) + '   '
        ans += "Ссылка на объявление: "+ str((vacancies[0][6])) + '   '
        split_ans = ans.split("   ")
        new_line_ans = '\n'.join(split_ans)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Еще вакансии")
        item2 = types.KeyboardButton("Фильтр")
        markup.add(item1, item2)
            
        bot.send_message(message.chat.id, str(new_line_ans),  reply_markup=markup)
    ##########
    # if vacancies[2] == 'пидор':
    #     bot.send_message(message.chat.id, vacancies)

    # else:
    #     for i in range(20):
    #         post_preprocess_vacancies = vacancies_to_string(vacancies[i])
    #         # print(post_preprocess_vacancies)
    #         post_preprocess_vacancies[1] = post_preprocess_vacancies[1]['name']
    #         post_preprocess_vacancies[2] = check_salary(post_preprocess_vacancies[2])
            
    #         post_preprocess_vacancies[3] = post_preprocess_vacancies[3]['name']
    #         post_preprocess_vacancies[4] = post_preprocess_vacancies[4]['name']
    #         vacancies_str = '\n'.join(post_preprocess_vacancies)
            
    #         bot.send_message(message.chat.id, vacancies_str)

bot.polling()