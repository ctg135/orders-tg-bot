from telebot import types

import db

category_1 = '🍲 Первые блюда'
category_2 = '🍝 Вторые блюда'
category_3 = '🥗 Салаты'
category_4 = '🧃 Напитки'

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
                    result += f'\n<i>{category_1}</i>\n'
                case 2:
                    result += f'\n<i>{category_2}</i>\n'
                case 3:
                    result += f'\n<i>{category_3}</i>\n'
                case 4:
                    result += f'\n<i>{category_4}</i>\n'
        result += f' {food.name} {food.price} руб.\n'
    return result

 