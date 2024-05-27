import sqlite3 as sl
from telebot import types
import telebot
from database import Adapter

API_KEY = ""

bot = telebot.TeleBot('{API_KEY}')

start_txt = 'Привет, {username}! Это - бот для поиска соседа по общаге'

data = sl.connect("forms.db")
friend_table = sl.connect("links.db")

with data:
    table = data.execute("select count(*) from sqlite_master where type='table'")
    for row in table:
        if (row[0] == 0):
            data.execute("""
                            CREATE TABLE users (
                                user_id VARCHAR(200),
                                user_name VARCHAR(200),
                                full_name VARCHAR(200),
                                form_was_created BOOL,
                                department VARCHAR(200),
                                age INT,
                                small_text VARCHAR(2000),
                                last_send VARCHAR(200),
                                status VARCHAR(200)
                            )
                         """)
            
with friend_table:
    table = friend_table.execute("select count(*) from sqlite_master where type='table'")
    for row in table:
        if (row[0] == 0):
            friend_table.execute("""
                            CREATE TABLE user_links (
                                first_user_id VARCHAR(200),
                                second_user_id VARCHAR(200)
                            )
                         """)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, start_txt.format(username=message.from_user.username))
    Adapter.add_user(UserId=message.from_user.id, UserName=message.from_user.username)
    if not Adapter.check_in(message.from_user.id):
        keyboard = types.InlineKeyboardMarkup()
        new_button = types.InlineKeyboardButton(text='Заполнить анкету', callback_data='registration')
        keyboard.add(new_button)
        bot.send_message(message.from_user.id, text='Для начала тебе необходимо заполнить анкету о себе', reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        new_button = types.InlineKeyboardButton(text='Варианты', callback_data='/help')
        keyboard.add(new_button)
        bot.send_message(message.from_user.id, text="У тебя есть анкета. Что будет делать дальше?", reply_markup=keyboard)
    
@bot.message_handler(commands=['help'])
def help(message):
    UserId = message.from_user.id
    status = Adapter.get_status(UserId)
    keyboard = types.InlineKeyboardMarkup()
    if Adapter.check_in(UserId):
        new_button = types.InlineKeyboardButton(text='Обновить анкету', callback_data='registration')
    else:
        new_button = types.InlineKeyboardButton(text='Заполнить анкету', callback_data='registration')
    keyboard.add(new_button)
    new_button = types.InlineKeyboardButton(text="Смотреть анкеты", callback_data="/look_for_neighbor")
    keyboard.add(new_button)
    bot.send_message(message.from_user.id, text="Варианты", reply_markup=keyboard)

@bot.message_handler(commands=["look_for_neighbor"])
def look_for(message):
    UserId = message.from_user.id
    status = Adapter.get_status(UserId)
    keyboard = types.InlineKeyboardMarkup()
    if not Adapter.check_in(UserId):
        form_button = types.InlineKeyboardButton(text='Заполнить анкету', callback_data='registration')
        keyboard.add(form_button)
        bot.send_message(message.from_user.id, text='Для начала тебе необходимо заполнить анкету о себе', reply_markup=keyboard)
        return
    user_form = Adapter.get_form(UserId)
    Adapter.update_parameter(UserId, 'last_send', user_form[0])
    good_button = types.InlineKeyboardButton(text='Хочу соседствовать', callback_data='link {user1} {user2}'.format(user1=str(UserId), user2=user_form[0]))
    keyboard.add(good_button)
    bad_button = types.InlineKeyboardButton(text='Заполнить анкету', callback_data='registration')


@bot.message_handler(content_types=["text"])
def get_data(message):
    UserId = message.from_user.id
    status = Adapter.get_status(UserId)
    if status == "Ask for name":
        Adapter.update_parameter(UserId, 'full_name', message.text)
        bot.send_message(UserId, text="Твое имя - {your_name}. Теперь напиши свой возраст(числом)".format(your_name=Adapter.get_full_name(UserId)))
        Adapter.update_parameter(UserId, 'status', 'Ask for age')
    elif status == 'Ask for age':
        try:
            age = int(message.text)
        except:
            bot.send_message(message.from_user.id, text="Неправильный формат. Введите возраст числом")
            return
        Adapter.update_parameter(UserId, 'age', age)
        bot.send_message(message.from_user.id, text="Хорошо. Теперь напиши физтех-школу, на которой ты учишься")
        Adapter.update_parameter(UserId, 'status', 'Ask for department')
    elif status == 'Ask for department':
        Adapter.update_parameter(UserId, 'department', message.text)
        bot.send_message(message.from_user.id, text="Отлично. Теперь напиши небольшой текст о себе, как о соседе")
        Adapter.update_parameter(UserId, 'status', 'Ask for small text')
    elif status == 'Ask for small text':
        Adapter.update_parameter(UserId, 'small_text', message.text)
        bot.send_message(message.from_user.id, text="На этом настройка анкеты завершена. Напиши '/help', чтобы посмотреть на возможные сценарии взаимодействия")
        Adapter.update_parameter(UserId, 'status', "Form is filled")
    else:
        bot.send_message(message.from_user.id, text="Я тебя не понимаю. Нажми '/help', чтобы посмотреть на возможные сценарии взаимодействия")


@bot.callback_query_handler(lambda callback: callback.data.startswith("registration"))
def start_register(callback: types.CallbackQuery):
    Adapter.update_parameter(callback.message.chat.id, "form_was_created", True)
    Adapter.update_parameter(callback.message.chat.id, 'status', 'Ask for name')
    bot.send_message(callback.message.chat.id, "Напиши свое полное имя\n")

@bot.callback_query_handler(func=lambda call: call.data == '/help')
def callback_help(call):
    bot.send_message(call.message.chat.id, "Нажми: /help")

@bot.callback_query_handler(func=lambda call: call.data == '/look_for_neighbor')
def callback_look_for_neighbor(call):
    UserId = call.message.chat.id
    status = Adapter.get_status(UserId)
    keyboard = types.InlineKeyboardMarkup()
    if not Adapter.check_in(UserId):
        form_button = types.InlineKeyboardButton(text='Заполнить анкету', callback_data='registration')
        keyboard.add(form_button)
        bot.send_message(UserId, text='Для начала тебе необходимо заполнить анкету о себе', reply_markup=keyboard)
        return
    user_form = Adapter.get_form(UserId)
    if (user_form[0] == '0'):
        form_button = types.InlineKeyboardButton(text='Смотреть анкеты', callback_data='/look_for_neighbor')
        keyboard.add(form_button)
        bot.send_message(UserId, text='Никого нет.... Жмакни еще раз', reply_markup=keyboard)
        return
    
    Adapter.update_parameter(UserId, 'last_send', user_form[0])
    good_button = types.InlineKeyboardButton(text='Хочу соседствовать', callback_data='link {user1} {user2}'.format(user1=str(UserId), user2=user_form[0]))
    keyboard.add(good_button)
    bad_button = types.InlineKeyboardButton(text='Смотреть дальше', callback_data='/look_for_neighbor')
    keyboard.add(bad_button)
    bot.send_message(UserId, text=user_form[1], reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("link"))
def callback_link(call):
    users = call.data.split()
    response = Adapter.link(users[1], users[2])
    keyboard = types.InlineKeyboardMarkup()
    good_button = types.InlineKeyboardButton(text='Смотреть анкеты дальше', callback_data='/look_for_neighbor')
    keyboard.add(good_button)
    if not response:
        bot.send_message(call.message.chat.id, text="Запрос отправлен", reply_markup=keyboard)
        good_button = types.InlineKeyboardButton(text='Хочу соседствовать', callback_data='link {user1} {user2}'.format(user1=str(users[2]), user2=str(users[1])))
        keyboard.add(good_button)
        form = Adapter.get_form_with_id(call.message.chat.id)
        bot.send_message(int(users[2]), text="Посмотрите анкету этого пользователя: \n{userform}\n".format(userform=form), reply_markup=keyboard)
    else:
        bot.send_message(call.message.chat.id, text="""Этот пользователь тоже хочет с вами соседствовать.
                          Его тг: @{username}""".format(username=Adapter.get_username(users[2])), reply_markup=keyboard)
        form = Adapter.get_form_with_id(call.message.chat.id)
        bot.send_message(int(users[2]), text="""Пользователь с этой анкетой хочет с вами соседствовать: \n{userform}\n 
                         Его тг: @{username}""".format(userform=form, username=Adapter.get_username(users[1])), reply_markup=keyboard)
    


if __name__ == '__main__':
    while True:
        bot.polling(none_stop=True, interval=0)