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
    id = -1
    category = 0
    name = ''
    price = 0
    visibility = 0


def check_database() -> None:
    '''
    Проверяет на наличие базу данных. В случае отсутствия создает новую пустую
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS `order` 
                (`id` INTEGER, `user_id` TEXT, `date` date, `telephone` TEXT, `order_list` TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS `menu` 
                (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `category` INTEGER, `name` TEXT UNIQUE, `price` INTEGER, `visibility` INTEGER DEFAULT 1)''')
    con.commit()

def menu_get_list_nice() -> list:
    '''
    Выгружает из базы данных список всех блюд, без скрытых
    '''
    result = []
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute('''SELECT id, category, name, price
                FROM menu 
                WHERE menu.visibility = 1
                ORDER BY category, id ASC;''')
    rows = cur.fetchall()
    for row in rows:
        f = Food()
        f.id = row[0]
        f.category = row[1]
        f.name = row[2]
        f.price = row[3]
        result.append(f)
    return result

def menu_get_list() -> list:
    '''
    Выгружает из базы данных список всех блюд
    '''
    result = []
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute('''SELECT id, category, name, price, visibility
                FROM menu 
                ORDER BY menu.category, menu.id ASC;''')
    rows = cur.fetchall()
    for row in rows:
        f = Food()
        f.id = row[0]
        f.category = row[1]
        f.name = row[2]
        f.price = row[3]
        f.visibility = row[4]
        result.append(f)
    return result

def menu_get_list_category(category: int) -> list:
    '''
    Получает список блюд из меню по одной категории
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute(f'''SELECT * FROM menu 
                    WHERE category = {category} 
                    ORDER BY `id` ASC;''')
    rows = cur.fetchall()
    result = []
    for row in rows:
        f = Food()
        f.id = row[0]
        f.category = row[1]
        f.name = row[2]
        f.price = row[3]
        f.visibility = row[4]
        result.append(f)
    return result

def menu_get_list_category_nice(category: int) -> list:
    '''
    Получает список блюд из меню по одной категории, без скрытых
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute(f'''SELECT * FROM menu 
                    WHERE category = {category} AND visibility = 1
                    ORDER BY `id` ASC;''')
    rows = cur.fetchall()
    result = []
    for row in rows:
        f = Food()
        f.id = row[0]
        f.category = row[1]
        f.name = row[2]
        f.price = row[3]
        f.visibility = row[4]
        result.append(f)
    return result


def menu_add_item(i: Food) -> None:
    '''
    Добавляет запись с новым блюдом
    # TODO добавить проверку на совпадение имени
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute(f'''INSERT INTO menu (category, name, price) 
                VALUES ({i.category}, "{i.name}", {i.price})''')
    con.commit()

def menu_edit_item(id: int, new: Food) -> None:
    '''
    Установка новых значений для поля
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute(f'''UPDATE menu
                SET name = '{new.name}', price = {new.price}, visibility = {new.visibility}
                WHERE id = {id};''')
    con.commit()

def menu_delete_item(id: int) -> None:
    '''
    Удаление элемента по id
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute(f'''DELETE FROM menu WHERE id = {id};''')
    con.commit()

def get_item(id) -> Food:
    '''
    Получение одного элемента из БД
    В случае отсутствия возвращает пустой элемент
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute(f'''SELECT * FROM menu 
                    WHERE id = {id};''')
    value = cur.fetchone()

    if value is None:
        return Food()
    
    result = Food()
    result.id = value[0]
    result.category = value[1]
    result.name = value[2]
    result.price = value[3]
    result.visibility = value[4]

    return result