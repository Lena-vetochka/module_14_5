# -*- coding: utf-8 -*-
import sqlite3


def initiate_db():
    connection = sqlite3.connect('not_telegram.db')  # подключаемся к бд
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INT,
    title TEXT NOT NULL,
    description TEXT,
    price INT NOT NULL
    );
    ''')

    # # добавляем значения
    # for i in range(1, 5):
    #     cursor.execute('INSERT INTO Products(id, title, description, price) VALUES (?, ?, ?, ?)',
    #                    (i, f'Продукт {i}', f'Описание {i}', int(f'{i}00')))

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER NOT NULL,
    balance INTEGER NOT NULL
    );
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON Users (email)')
    connection.commit() #сохраняем
    connection.close()  #закрываем БД


def get_all_products():
    initiate_db()
    connection = sqlite3.connect('not_telegram.db')  # подключаемся к бд
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Products')  #все продукты
    return (cursor.fetchall())
    connection.close()  # закрываем БД


def add_user(username, email, age):
    connection = sqlite3.connect('not_telegram.db')  # подключаемся к бд
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO Users (username, email, age, balance) VALUES ('{username}', '{email}', '{age}', 1000)")
    # добавляем пользователя с указанными параметрами
    connection.commit()
    connection.close()


def is_included(username):
    connection = sqlite3.connect('not_telegram.db')  # подключаемся к бд
    cursor = connection.cursor()
    check_username = cursor.execute('SELECT * FROM Users WHERE username=?', (username,))
    if check_username.fetchone() is None:  #если пользователя нет
        return True
    else:
        return False
    connection.commit()
    connection.close()


