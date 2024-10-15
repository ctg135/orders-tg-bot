import datetime
from telebot import types

import db

category_1 = '🍲 Первые блюда'
category_2 = '🍝 Вторые блюда'
category_3 = '🥗 Салаты'
category_4 = '🧃 Напитки'

button_make_order = '📖 Сделать заказ'

def get_hello_admin_keyboard():
    '''
    Клавиатура приветствия с основными действиями бота
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu = types.KeyboardButton(text='/menu')
    result.add(menu)
    return result

def get_hello_client_keyboard():
    '''
    Клавиатура приветствия клиента
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu = types.KeyboardButton(text=button_make_order)
    result.add(menu)
    return result

def get_menu_add_keyboard():
    '''
    Клавиатура для пустого меню
    '''
    result = types.InlineKeyboardMarkup()
    add = types.InlineKeyboardButton(text='➕', callback_data='menu_add')
    result.add(add)
    return result

def get_menu_keyboard():
    '''
    Клавиатура для редактирования меню
    '''
    result = types.InlineKeyboardMarkup()
    add = types.InlineKeyboardButton(text='➕', callback_data='menu_add')
    edit = types.InlineKeyboardButton(text='📝', callback_data='menu_edit')
    delete = types.InlineKeyboardButton(text='🗑️', callback_data='menu_delete')
    result.add(add, edit, delete)
    return result

def get_menu_category_keyboard():
    '''
    Клавиатура для получения категории блюда
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cat_1 = types.KeyboardButton(text=category_1)
    cat_2 = types.KeyboardButton(text=category_2)
    cat_3 = types.KeyboardButton(text=category_3)
    cat_4 = types.KeyboardButton(text=category_4)
    result.add(cat_1, cat_2)
    result.add(cat_3, cat_4)
    return result

def get_menu_id_category_keyboard(menu: db.Food) -> types.InlineKeyboardMarkup:
    '''
    Клавиатура с id записи
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item in menu:
        result.add(types.KeyboardButton(text=item.id))
    return result

def get_ok_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура с надписью Ок
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ok = types.KeyboardButton(text='Ок')
    result.add(ok)
    return result



def get_hello_admin_text() -> str:
    '''
    Текст для справки администратору
    '''
    return 'Для просмотра меню нажмите /menu'

def get_hello_client_text() -> str:
    '''
    Текст приветствия пользователя
    '''
    return '''
👋 Здравствуйте, вас приветсвтует Пищепром!
📝 Прием заказов на обед до 11; доставка обедов с 13 до 14 🕐'''

def get_hello_client_late_text() -> str:
    '''
    Текст приветствия пользователя (после времени принятия заказа)
    '''
    return 'Хотите оформить доставку на завтра?'

def format_menu_list(menu: db.Food) -> str:
    '''
    Возвращает отформатированный список меню
    '''
    result = ''
    last_category = 0
    for food in menu:
        if food.category != last_category:
            last_category = food.category
            match last_category:
                case 1:
                    result += f'\n<b>{category_1}</b>\n'
                case 2:
                    result += f'\n<b>{category_2}</b>\n'
                case 3:
                    result += f'\n<b>{category_3}</b>\n'
                case 4:
                    result += f'\n<b>{category_4}</b>\n'
        result += f' {food.name} <i>{food.price} руб.</i>\n'
    return result

def format_menu_list_id(menu: db.Food) -> str:
    '''
    Возвращает отформатированный список меню с id (для редактирования и удаления)
    '''
    result = ''
    last_category = 0
    for food in menu:
        if food.category != last_category:
            last_category = food.category
            match last_category:
                case 1:
                    result += f'\n<b>{category_1}</b>\n'
                case 2:
                    result += f'\n<b>{category_2}</b>\n'
                case 3:
                    result += f'\n<b>{category_3}</b>\n'
                case 4:
                    result += f'\n<b>{category_4}</b>\n'
        result += f'{food.id}. {food.name} <i>{food.price} руб.</i>\n'
    return result
