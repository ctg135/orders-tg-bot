import sqlite3
import os.path
from datetime import date, datetime

FILE_DB='orders.db'

def check_database():
    '''
    Проверяет на наличие базу данных. В случае отсутствия создает новую пустую
    '''
    con = sqlite3.connect(FILE_DB)
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS `order` (`id` INTEGER, `user_id` TEXT, `date` date, `telephone` TEXT, `order_list` TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS `menu` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `category` INTEGER UNIQUE, `name` INTEGER UNIQUE, `price` INTEGER UNIQUE)')
    con.commit()


