import telebot
from telebot import types
import requests
import math

token = "7418667479:AAHCK0hHCnzZ3pVAz9d-HRE1UvpRLoIQVuA"

bot = telebot.TeleBot(token)

user_states = {} # состояние пользователя

number_of_output_vacancies = 5
vacancies_from_bd = []
last_idx = 0
count_vacancies = 0

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Искать вакансию")
    markup.add(item1)
    bot.send_message(message.chat.id, 'Привет, тебя приветствует 💻WORKbot💻 Самый простой и удобный способ найти для себя лучшую вакансию.'
                     'Скорее жми на кнопку "Искать вакансию"👨‍💼🙈👩‍💼', reply_markup=markup)
    user_states[message.chat.id] = 'предложить_поиск_вакансий' # переход на страницу поиска вакансий


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'предложить_поиск_вакансий')
def answer(message):
    user_text = message.text
    if user_text == "Искать вакансию":
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Напишите название вакансии, которая вас интересует",reply_markup=markup)
        user_states[message.chat.id] = 'вывод_вакансии'
    else:
        bot.send_message(message.chat.id, "нажмите кнопку")
        user_states[message.chat.id] = 'предложить_поиск_вакансий'


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'вывод_вакансии')
def answer(message):
    user_text = message.text
    url = "http://127.0.0.1:5000/get_count_vacancies_bd"

    # Параметры запроса
    params = {
        'vacancy_name': user_text,
        'search_field': 'name'  # Опционально
    }

    # Выполнение GET запроса
    response = requests.get(url, params=params)

   
    if response.status_code == 200:
        vacancies_count = response.json()[0][0]
        if vacancies_count==0:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Искать вакансию")
            markup.add(item1)
            bot.send_message(message.chat.id, "вакансий не найдено, попробуйте ввести другую", reply_markup=markup)
            user_states[message.chat.id] = 'предложить_поиск_вакансий'
            return
        else:
            global count_vacancies
            count_vacancies = vacancies_count
            bot.send_message(message.chat.id, f'Локально найдено {vacancies_count} вакансий')
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Искать вакансию")
        markup.add(item1)
        bot.send_message(message.chat.id, "возникла непредвиденная ошибка, попробуйте ввести название заново", reply_markup=markup)
        user_states[message.chat.id] = 'предложить_поиск_вакансий'
        return
    

    url = "http://127.0.0.1:5000/get_vacancies_bd"

    # Параметры запроса
    params = {
        'vacancy_name': user_text,
        'search_field': 'name'  # Опционально
    }

    # Выполнение GET запроса
    response = requests.get(url, params=params)
    vacancies_from_bd_all = response.json()
    if len(vacancies_from_bd_all) > number_of_output_vacancies:
        output = vacancies_from_bd_all[:number_of_output_vacancies]
        vacancies_from_bd = {number_of_output_vacancies: vacancies_from_bd_all[number_of_output_vacancies:]}

    global last_idx

    for cnt in range(number_of_output_vacancies):
        ans = ''
        for i in range(1,10):
            if i == 2 :
                ans += 'Город: ' + str((output[cnt][i])) + '   '
            if i == 1:
                ans += f"Вакансия № {last_idx+1}: " + str((output[cnt][i])) + '   '
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
        bot.send_message(message.chat.id, str(new_line_ans))
        last_idx += 1

    
    user_states[message.chat.id] = 'поиск_апи_или_вакансии_из_бд'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Больше локальных вакансий")
    item2 = types.KeyboardButton("Искать на охотнике за головами")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Посмотреть ещё локальные вакансии или искать на охотнике за головами', reply_markup=markup)
    return


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'поиск_апи_или_вакансии_из_бд')
def handle_button_press(message):
    print(message.text)
    
    if message.text == "Больше локальных вакансий":
        bot.send_message(message.chat.id, "dev1")
        user_states[message.chat.id] = 'Больше_вакансий_из_бд'
        more_vacancy_from_bd(message)
        return
    else: #message.text == "Искать на охотнике за головами":
        bot.send_message(message.chat.id, "de2")
        user_states[message.chat.id] = 'апи_хх_ру'
        api_hh_ru(message)
        return
    # bot.send_message(message.chat.id, "dev")
    

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'Больше_вакансий_из_бд')
def more_vacancy_from_bd(message):
    bot.send_message(message.chat.id, "локально найдено столько вакансий")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'апи_хх_ру')
def api_hh_ru(message):
    bot.send_message(message.chat.id, "Искать на охотнике за головами")

    
    # vac = user_text.split(' ')[-1]#для случая запроса - Еще локальные вакансии "..."
    
    # if user_text != f"Еще локальные вакансии {vac}":
    #     cnt_local = vacancies[-1][-1][-1] #количество локальных запросов
    # else:
    #     response = requests.get(url, params = {
    #                                             'vacancy_name': vac,
    #                                             'search_field': 'name' })
    #     vacancies = response.json()
    #     cnt_local = vacancies[-1][-1][-1]# Еще локальные вакансии {vac} найти для vac количество

    # if user_text == 'Искать вакансию':
    #     bot.send_message(message.chat.id, "Напишите название вакансии, которая вас интересует")
    # elif user_text != f"Еще локальные вакансии {vac}" and cnt_local == 0 :
    #     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #     item1 = types.KeyboardButton("Новые вакансии через API")
    #     markup.add(item1) 
    #     bot.send_message(message.chat.id, 'Локально вакансий по такому запросу нет, хотите обратиться к API, тогда скорее жмите на "Новые вакансии через API"',  reply_markup=markup)
    # else:
    #     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #     item1 = types.KeyboardButton(f"Еще локальные вакансии {vac}")
    #     item2 = types.KeyboardButton("Фильтр")
    #     markup.add(item1, item2)

    #     cnt_to_output = math.ceil(cnt_local / 2)

    #     if user_text != f"Еще локальные вакансии {vac}":
    #         bot.send_message(message.chat.id, f'Локально найдено {cnt_local} вакансий',  reply_markup=markup)
        
    #     s, e = 0, cnt_to_output#start, end - какой промежуток вакансий выводить
    #     if user_text == f'Еще локальные вакансии {vac}' and cnt_local != 1:
    #         s, e = cnt_to_output, cnt_local
        
    
            
    #         if (user_text == f'Еще локальные вакансии {vac}' and cnt == e-1) or cnt_local == 1 :
    #             markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #             item1 = types.KeyboardButton(f"API {vac}")
    #             item2 = types.KeyboardButton("Фильтр")
    #             markup.add(item1, item2)
    #             bot.send_message(message.chat.id, f'Локальных вакансий больше не осталось, но ты можешь обратиться к API, жми скорее кнопку "API {vac}"',  reply_markup=markup)
    
bot.polling()  
    
    
    
    
    
    
    
    
    
    ##########

#     def check_salary(data):
#     if data is None:
#         return "О зарплате нет данных"
#     for key, value in data.items():
#         if key == 'to' and value != None:
#             return(f'до {data[key]} RUR')
#     return 'Размер зарплаты обсуждается лично'

# def vacancies_to_string(vacancies):
#     """
#     Преобразует список вакансий в строку, где каждая вакансия представлена в виде строки,
#     содержащей значения её полей, разделенных символом новой строки"""
#     result = [vacancies['name'],vacancies['area'],  vacancies['salary'],  vacancies['experience'],vacancies['employment'],  vacancies['alternate_url']]
 
#     return result
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