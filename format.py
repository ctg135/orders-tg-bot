import datetime
from telebot import types

import db

category_1 = '🍲 Первые блюда'
category_2 = '🍝 Гарниры'
category_3 = '🍖 Мясное'
category_4 = '🥗 Салаты'
category_5 = '🧃 Напитки'

button_ok = 'Ок'
button_back = '↩️ Назад'

button_menu_nice = 'Меню дня'
button_menu_full = 'Полный перечень'
button_menu_hidden = 'Скрыть'
button_menu_visible = 'Указать'

button_init_order = '📖 Сделать заказ'
button_make_order = '✅ Заказ собран'
button_cart = 'Корзина'
button_cart_clear = 'Очистить корзину'
button_category_1 = '🍲 Первые блюда'
button_category_2 = '🍝 Вторые блюда'
button_category_3 = '🥗 Салаты'
button_category_4 = '🧃 Напитки'

def get_hello_admin_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура приветствия с основными действиями бота
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_nice = types.KeyboardButton(text=button_menu_nice)
    menu_full = types.KeyboardButton(text=button_menu_full)
    result.add(menu_nice, menu_full)
    return result

def get_hello_client_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура приветствия клиента
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu = types.KeyboardButton(text=button_init_order)
    result.add(menu)
    return result

def get_menu_add_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура для пустого меню
    '''
    result = types.InlineKeyboardMarkup()
    add = types.InlineKeyboardButton(text='➕', callback_data='menu_add')
    result.add(add)
    return result

def get_menu_edit_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура для редактирования меню
    '''
    result = types.InlineKeyboardMarkup()
    add = types.InlineKeyboardButton(text='➕', callback_data='menu_add')
    edit = types.InlineKeyboardButton(text='📝', callback_data='menu_edit')
    delete = types.InlineKeyboardButton(text='🗑️', callback_data='menu_delete')
    result.add(add, edit, delete)
    return result

def get_menu_category_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура для получения категории блюда
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cat_1 = types.KeyboardButton(text=category_1)
    cat_2 = types.KeyboardButton(text=category_2)
    cat_3 = types.KeyboardButton(text=category_3)
    cat_4 = types.KeyboardButton(text=category_4)
    cat_5 = types.KeyboardButton(text=category_5)
    back = types.KeyboardButton(text=button_back)
    result.add(cat_1, cat_2)
    result.add(cat_3, cat_4)
    result.add(cat_5, back)
    return result

def get_menu_id_category_keyboard(menu: list) -> types.InlineKeyboardMarkup:
    '''
    Клавиатура с id записи
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item in menu:
        result.add(types.KeyboardButton(text=item.id))
    return result

def get_menu_keyboard(menu: list) -> types.InlineKeyboardMarkup:
    '''
    Клавиатура с названиями блюд
    Для преобразования обратно используется get_id_from_name(menu, name)
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    lefts = menu[::2]
    rights = menu[1::2]
    for left, right in zip(lefts, rights):
        result.add(left.name, right.name)
    if len(menu) % 2 == 1: 
        result.add(types.KeyboardButton(text=lefts[-1].name))
    result.add(types.KeyboardButton(text=button_back))
    return result

def get_numbers_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура с числами [1-9] и кнопкой "Назад"
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    num1 = types.KeyboardButton(text='1')
    num2 = types.KeyboardButton(text='2')
    num3 = types.KeyboardButton(text='3')
    num4 = types.KeyboardButton(text='4')
    num5 = types.KeyboardButton(text='5')
    num6 = types.KeyboardButton(text='6')
    num7 = types.KeyboardButton(text='7')
    num8 = types.KeyboardButton(text='8')
    num9 = types.KeyboardButton(text='9')
    back = types.KeyboardButton(text=button_back)
    result.add(num1, num2, num3)
    result.add(num4, num5, num6)
    result.add(num7, num8, num9)
    result.add(back)
    return result

def get_menu_visibility_edit_keyobard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура для получения видимости пункта
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    hidden = types.KeyboardButton(text=button_menu_hidden)
    visible = types.KeyboardButton(text=button_menu_visible)
    ok = types.KeyboardButton(text=button_ok)
    result.add(visible, hidden)
    result.add(ok)
    return result

def get_ok_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура с надписью Ок
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ok = types.KeyboardButton(text='Ок')
    result.add(ok)
    return result

def get_order_start_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Основная клавиатура для сборки заказа
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    basket = types.KeyboardButton(text=button_cart)
    make_order = types.KeyboardButton(text=button_make_order)
    back = types.KeyboardButton(text=button_back)
    cat_1 = types.KeyboardButton(text=button_category_1)
    cat_2 = types.KeyboardButton(text=button_category_2)
    cat_3 = types.KeyboardButton(text=button_category_3)
    cat_4 = types.KeyboardButton(text=button_category_4)
    result.add(basket, make_order)
    result.add(cat_1, cat_2)
    result.add(cat_3, cat_4)
    result.add(back)
    return result

def get_cart_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура меню корзины
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clear = types.KeyboardButton(text=button_cart_clear)
    make_order = types.KeyboardButton(text=button_make_order)
    back = types.KeyboardButton(text=button_back)
    result.add(back, clear)
    result.add(make_order)
    return result

def get_cart_list_keyboard(cart: map):
    '''
    Клавиатура для списка выбранных товаров
    '''
    return None

def get_hello_admin_text() -> str:
    '''
    Текст для справки администратору
    '''
    return f'''
<code>{button_menu_nice}</code> - список меню, как он отображается клиенту
<code>{button_menu_full}</code> - полное меню
'''

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

def get_menu_no_items_text() -> str:
    '''
    Текст отсутствия меню (у клиента)
    '''
    return 'Извините, данное меню еще не заполнено. Попробуйте сделать заказ позже'

def get_cart_help_text() -> str:
    '''
    Вспомогательный текст для корзины
    '''
    return '''
Измените количество при помощи ➕ и ➖
Нажмите на ❌ для удаления одной позиции
'''

def format_menu_list_full(menu: db.Food) -> str:
    '''
    Возвращает отформатированный список меню, со знаком скрытости
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
                case 5:
                    result += f'\n<b>{category_5}</b>\n'
        result += f'  {food.name} <i>{food.price} руб.</i> { "" if food.visibility else "🫣" } n'
    return result

def format_menu_list_nice(menu: list) -> str:
    '''
    Возвращает отформатированный список меню
    '''
    if len(menu) == 0:
        return 'Пока нету позиций'

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
                case 5:
                    result += f'\n<b>{category_5}</b>\n'
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
                case 5:
                    result += f'\n<b>{category_5}</b>\n'
        result += f'{food.id}. {food.name} <i>{food.price} руб.</i> {"" if food.visibility else "🫣" }\n'
    return result

def format_cart_list(cart: map) -> str:
    '''
    Возвращает список товаров из корзины
    '''
    if len(cart) == 0:
        return 'Ваша корзина пуста'

    result = ''
    counter = 1
    summary = 0
    for id, count in cart.items():
        id_temp = str(id)
        if id_temp.isdigit():
            item = db.get_item(id)
            cost = item.price * count
            summary += cost
            counter += 1
            result += f'{counter}. <b>{item.name}</b> ({item.price} руб.) x <b>{count}</b> = {cost} руб.\n\n'
        else:
            ids = id_temp.split('+')
            items = [db.get_item(ids[0]), db.get_item(ids[1])]
            cost = (items[0].price + items[1].price) * count
            summary += cost
            counter += 1
            result += f'{counter}. <b>{items[0].name} с {items[1].name}</b> ({items[0].price + items[1].price} руб.) x <b>{count}</b> = {cost} руб.\n\n'
    result += f'Общая сумма заказа: {summary} руб.'
    return result


def get_id_from_name(menu: list, name: str) -> int:
    '''
    Из названия получает id блюда
    Для клавиатуры - get_menu_keyboard(menu)
    '''
    id = 0
    for item in menu:
        if item.name == name:
            id = item.id
    return id
