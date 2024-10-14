import sqlite3
from datetime import date, datetime

FILE_DB='orders.db'

class Food:
    '''
    Категории:
    1 - Первое блюдо
    2 - Второе блюдо
    3 - Салат
    4 - Напиток
    '''
    id = 0
    category = 0
    name = ''
    price = 0


def check_database() -> None:
    '''
    Проверяет на наличие базу данных. В случае отсутствия создает новую пустую
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS `order` (`id` INTEGER, `user_id` TEXT, `date` date, `telephone` TEXT, `order_list` TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS `menu` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `category` INTEGER UNIQUE, `name` INTEGER UNIQUE, `price` INTEGER UNIQUE)')
    con.commit()

def get_menu_list() -> list:
    '''
    Выгружает из базы данных список всех блюд
    '''
    result = []
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute('SELECT id, category, name, price FROM menu ORDER BY menu.category, menu.id ASC;')
    rows = cur.fetchall()
    for row in rows:
        f = Food()
        f.id = row[0]
        f.category = row[1]
        f.name = row[2]
        f.price = row[3]
        result.append(f)
    return result


