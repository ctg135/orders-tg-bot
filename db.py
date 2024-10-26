import sqlite3
from datetime import date, datetime

FILE_DB='orders.db'

'''
Статусы заказов:
0 - Только что создан
1 - Принят
2 - Отменён
'''

class Food:
    '''
    Категории:
    1 - Первое блюдо
    2 - Гарнир
    3 - Мясное
    4 - Салат
    5 - Напиток
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
                (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `user_id` TEXT, `date` date, `telephone` TEXT, `address` TEXT, `order_list` TEXT, status INTEGER DEFAULT 0)''')
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

def get_telephone_from_last_order(user_id: int) -> str:
    '''
    Возвращает последний использованный номер телефона
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute(f'''SELECT id, telephone FROM `order` 
                    WHERE user_id = {user_id} 
                    ORDER BY id DESC;''')
    value = cur.fetchone()

    if value is None: return ''
    else: return value[1]

def get_address_from_last_order(user_id: int) -> str:
    '''
    Возвращает последний использованный адрес
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute(f'''SELECT id, address FROM `order` 
                    WHERE user_id = {user_id} 
                    ORDER BY id DESC;''')
    value = cur.fetchone()

    if value is None: return ''
    else: return value[1]

def order_add(user_id: int, telephone: str, address: str, order_list: str, date: datetime = datetime.now()) -> int:
    '''
    Добавляет запись с заказом в базу данных
    Возвращает номер созданного заказа
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute(f'''INSERT INTO `order` (user_id, date, telephone, address, order_list) 
                VALUES ("{user_id}", "{date.strftime("%d.%m.%Y %H:%M:%S")}", "{telephone}", "{address}", "{order_list}")''')
    con.commit()
    
    cur.execute(f'''SELECT id 
                    FROM`order` 
                    WHERE user_id = {user_id} 
                    ORDER BY id DESC;''')
    return int(cur.fetchone()[0])

def order_get_user_id(id: int) -> int:
    '''
    По номеру заказа возвращает id клиента
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute(f'''SELECT user_id FROM `order` 
                    WHERE id = {id};''')
    value = cur.fetchone()

    if value is None: return 0
    else: return value[0]

def order_change_status(id: int, status: int) -> None:
    '''
    Меняет статус заказа
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()    
    cur.execute(f'''UPDATE `order`
                SET status = {status}
                WHERE id = {id};''')
    con.commit()

def order_accept(id: int) -> int:
    '''
    Делает отметку в БД, что заказ принят
    Возвращает id клиента
    '''
    order_change_status(id, 1)
    return order_get_user_id(id)
    
def order_cancel(id: int) -> int:
    '''
    Делает отметку в БД, что заказ отменен
    Возвращает id клиента
    '''
    order_change_status(id, 2)
    return order_get_user_id(id)
    

    