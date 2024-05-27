import sqlite3 as sl
from random import choice

def is_empty(answer):
    s = ''
    for row in answer:
        s = s + '*'
    if (s == ''):
        return True
    else:
        return False

class Adapter:
    @staticmethod
    def add_user(UserId, UserName):
        data = sl.connect("forms.db")
        text_for_insert = """INSERT INTO users (user_id, user_name, full_name, form_was_created, department, age, small_text, last_send, status) 
                        values('{id}', '{name}', '', False, '', 0, '', '', '')"""
        with data:
            user_row = data.execute("SELECT * FROM users WHERE user_id='{id}'".format(id=str(UserId)))
            if (is_empty(user_row)):
                data.execute(text_for_insert.format(id=str(UserId), name=str(UserName)))

    @staticmethod
    def update_parameter(UserId, parameter_name, new_value):
        data = sl.connect("forms.db")
        if (type(new_value) == str):
            text_for_update = """UPDATE users SET '{column}' = '{value}' WHERE user_id='{id}'"""
        else:
            text_for_update = """UPDATE users SET '{column}' = {value} WHERE user_id='{id}'"""
        with data:
            data.execute(text_for_update.format(column=str(parameter_name), value=str(new_value), id=str(UserId)))
        
    @staticmethod
    def get_status(UserId):
        data = sl.connect("forms.db")
        with data:
            user_row = data.execute("SELECT status FROM users WHERE user_id='{id}'".format(id=str(UserId)))
        status = ''
        for row in user_row:
            status = status + str(row[0])
        return status
    
    @staticmethod
    def get_full_name(UserId):
        data = sl.connect("forms.db")
        with data:
            user_row = data.execute("SELECT full_name FROM users WHERE user_id='{id}'".format(id=str(UserId)))
        full_name = ''
        for row in user_row:
            full_name = full_name + str(row[0])
        return full_name
    
    @staticmethod
    def get_department(UserId):
        data = sl.connect("forms.db")
        with data:
            user_row = data.execute("SELECT department FROM users WHERE user_id='{id}'".format(id=str(UserId)))
        full_name = ''
        for row in user_row:
            full_name = full_name + str(row[0])
        return full_name
    
    @staticmethod
    def get_username(UserId):
        data = sl.connect("forms.db")
        with data:
            user_row = data.execute("SELECT user_name FROM users WHERE user_id='{id}'".format(id=str(UserId)))
        full_name = ''
        for row in user_row:
            full_name = full_name + str(row[0])
        return full_name

    @staticmethod
    def get_age(UserId):
        data = sl.connect("forms.db")
        with data:
            user_row = data.execute("SELECT age FROM users WHERE user_id='{id}'".format(id=str(UserId)))
        for row in user_row:
            return int(row[0])
        
    @staticmethod
    def check_in(UserId):
        data = sl.connect("forms.db")
        with data:
            user_row = data.execute("SELECT form_was_created FROM users WHERE user_id='{id}'".format(id=str(UserId)))
        for row in user_row:
            return bool(row[0])
        
    @staticmethod
    def get_form(UserId):
        data = sl.connect("forms.db")
        messages = []
        with data:
            table = data.execute("SELECT user_id, full_name, age, department, small_text FROM users WHERE form_was_created = True")
            for row in table:
                if row[0] != str(UserId):
                    new_message = "Имя: {FullName}\nВозраст: {Age}\nФизтех-школа: {Department}\nИнфо: {info}\n".format(FullName=row[1], Age=str(row[2]), Department=row[3], info=row[4])
                    messages.append([row[0], new_message])
        if (len(messages) == 0):
            return ['0', '0']
        return choice(messages)
    
    @staticmethod
    def get_form_with_id(UserId):
        data = sl.connect("forms.db")
        with data:
            table = data.execute("SELECT user_id, full_name, age, department, small_text FROM users WHERE user_id = '{id}'".format(id=UserId))
            for row in table:
                new_message = "Имя: {FullName}\nВозраст: {Age}\nФизтех-школа: {Department}\nИнфо: {info}\n".format(FullName=row[1], Age=str(row[2]), Department=row[3], info=row[4])
                return new_message
    
    @staticmethod
    def link(User1, User2):
        data = sl.connect("links.db")
        text_for_insert = "INSERT INTO user_links (first_user_id, second_user_id) values('{id1}', '{id2}')".format(id1=User1, id2=User2)
        with data:
            data.execute(text_for_insert)
        with data:
            response = data.execute("SELECT * FROM user_links WHERE first_user_id='{id1}' AND second_user_id='{id2}'".format(id1=User2, id2=User1))
            return not is_empty(response)
