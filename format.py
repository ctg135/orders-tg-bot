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

button_hello_text = 'Приветствие'
button_menu_nice = 'Меню дня'
button_menu_full = 'Полный перечень'
button_admins = 'Администраторы'
button_menu_hidden = 'Скрыть'
button_menu_visible = 'Указать'
button_order_accept = '✅ Принять'
button_order_cancel = '❌ Отмена'

button_init_order = '📖 Сделать заказ'
button_make_order = '✅ Заказ собран'
button_cart = 'Корзина'
button_cart_clear = 'Очистить корзину'
button_category_1 = '🍲 Первые блюда'
button_category_2 = '🍝 Вторые блюда'
button_category_3 = '🥗 Салаты'
button_category_4 = '🧃 Напитки'

def get_hello_admin_keyboard() -> types.ReplyKeyboardMarkup:
    '''
    Клавиатура приветствия с основными действиями бота
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_nice = types.KeyboardButton(text=button_menu_nice)
    menu_full = types.KeyboardButton(text=button_menu_full)
    hello_text = types.KeyboardButton(text=button_hello_text)
    admins = types.KeyboardButton(text=button_admins)
    result.add(menu_nice, menu_full)
    result.add(hello_text, admins)
    return result

def get_hello_client_keyboard() -> types.ReplyKeyboardMarkup:
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

def get_menu_category_keyboard() -> types.ReplyKeyboardMarkup:
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

def get_menu_id_category_keyboard(menu: list) -> types.ReplyKeyboardMarkup:
    '''
    Клавиатура с id записи
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item in menu:
        result.add(types.KeyboardButton(text=item.id))
    return result

def get_menu_keyboard(menu: list) -> types.ReplyKeyboardMarkup:
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

def get_numbers_keyboard() -> types.ReplyKeyboardMarkup:
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

def get_menu_visibility_edit_keyobard() -> types.ReplyKeyboardMarkup:
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

def get_ok_keyboard() -> types.ReplyKeyboardMarkup:
    '''
    Клавиатура с надписью Ок
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ok = types.KeyboardButton(text=button_ok)
    result.add(ok)
    return result

def get_back_keyboard() -> types.ReplyKeyboardMarkup:
    '''
    Клавиатура с надписью Назад
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton(text=button_back)
    result.add(back)
    return result

def get_order_start_keyboard() -> types.ReplyKeyboardMarkup:
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

def get_cart_keyboard() -> types.ReplyKeyboardMarkup:
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

def get_order_ok_keyboard() -> types.ReplyKeyboardMarkup:
    '''
    Клавиатура подтверждения заказа
    '''
    result = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ok = types.KeyboardButton(text=button_ok)
    back = types.KeyboardButton(text=button_back)
    result.add(ok, back)
    return result

def get_order_telephone_keyboard(telephone: str = '') -> types.ReplyKeyboardMarkup:
    '''
    Клавиатура для набора телефона заказа
    Подставляет изначальный телефон, если присутсвтует
    '''
    if telephone == '':
        result = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back = types.KeyboardButton(text=button_back)
        result.add(back)
        return result
    else:
        result = types.ReplyKeyboardMarkup(resize_keyboard=True)
        tel = types.KeyboardButton(text=telephone)
        back = types.KeyboardButton(text=button_back)
        result.add(tel)
        result.add(back)
        return result

def get_order_address_keyboard(address: str = '') -> types.ReplyKeyboardMarkup:
    '''
    Клавиатура для набора адреса доставки заказа
    Подставляет изначальный адрес, если присутсвтует
    '''
    if address == '':
        result = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back = types.KeyboardButton(text=button_back)
        result.add(back)
        return result
    else:
        result = types.ReplyKeyboardMarkup(resize_keyboard=True)
        adr = types.KeyboardButton(text=address)
        back = types.KeyboardButton(text=button_back)
        result.add(adr)
        result.add(back)
        return result

def get_cart_edit_keyboard(cart: map) -> types.InlineKeyboardMarkup:
    '''
    Клавиатура для редактирования корзины в заказе
    '''
    result = types.InlineKeyboardMarkup()
    counter = 1
    for id, count in cart.items():
        item_delete = ''
        if '+' in str(id):
            ids = id.split('+')
            items = [db.get_item(ids[0]), db.get_item(ids[1])]
            item_delete = types.InlineKeyboardButton(
                text=f'{counter}. ❌ {items[0].name} с {items[1].name}', 
                callback_data=f'cart_delete_{id}')
        else:
            item = db.get_item(id)
            item_delete = types.InlineKeyboardButton(
                text=f'{counter}. ❌ {item.name}', 
                callback_data=f'cart_delete_{id}')
        item_plus = types.InlineKeyboardButton(
            text='➕', 
            callback_data=f'cart_plus_{id}')
        item_minus = types.InlineKeyboardButton(
            text='➖', 
            callback_data=f'cart_minus_{id}')
        item_count = types.InlineKeyboardButton(
            text=str(count), 
            callback_data=f'cart_delete_{id}')
        result.add(item_delete)
        result.add(item_plus, item_count, item_minus)
        counter += 1
    return result

def get_ordered_accept_keyboard(number: int) -> types.InlineKeyboardMarkup:
    '''
    Клавиатура для принятия или отмены заказа оператором
    '''
    result = types.InlineKeyboardMarkup()
    accept = types.InlineKeyboardButton(text=button_order_accept, 
                                        callback_data=f'order_accept_{number}')
    cancel = types.InlineKeyboardButton(text=button_order_cancel, 
                                        callback_data=f'order_cancel_{number}')
    result.add(accept, cancel)
    return result

def get_admin_list_edit_keyboard() -> types.InlineKeyboardMarkup:
    '''
    Клавиатура для изменения списка администраторов
    '''
    result = types.InlineKeyboardMarkup()
    add_admin = types.InlineKeyboardButton(text='➕ Добавить', 
                                     callback_data='admin_add')
    result.add(add_admin)

    admins = db.get_admins()
    for admin in admins:
        admin_option = types.InlineKeyboardButton(text=f'{admin[1]} ❌', 
                                        callback_data=f'admin_delete_{admin[0]}')
        result.add(admin_option)
    return result
    

def get_hello_admin_text() -> str:
    '''
    Текст для справки администратору
    '''
    return f'''
<code>{button_menu_nice}</code> - список меню, как он отображается клиенту
<code>{button_menu_full}</code> - полное меню
<code>{button_hello_text}</code> - редактирование приветствия бота
<code>{button_admins}</code> - список администраторов бота
'''

def get_hello_client_text() -> str:
    '''
    Текст приветствия пользователя
    '''
    return db.get_message_hello_text()

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

def get_cart_empty_text() -> str:
    '''
    Текст при попытке выполнить заказ с пустой корзиной
    '''
    return '''
Ваша корзина пуста. Сначала выберите что-нибудь 😉
'''

def get_order_ok_text(cart: map):
    '''
    Текст для подтвежждения, что пользователь готов делать заказ
    '''
    return f'''
Готовы заказывать?
    
Ваш заказ:
{format_cart_list(cart)}
'''

def get_order_telephone_text(telephone: str = '') -> str:
    '''
    Текст для запроса у пользователя номера телефона
    '''
    if telephone == '':
        return 'Укажите номер телефона для проверки заказа 📲'
    else:
        return f'''
Укажите номер телефона для проверки заказа 📲

Последний использованный: <code>{telephone}</code>
'''
    
def get_order_address_text(address: str = '') -> str:
    '''
    Текст для запроса у пользователя адреса доставки
    '''
    if address == '':
        return 'Укажите адрес доставки 🚗'
    else:
        return f'''
Укажите адрес доставки 🚗

Последнй использованный:
<i>{address}</i>
'''

def get_ordered_user_text(number: int):
    '''
    Текст для отправки пользователю создания заказа
    '''
    return f'''
Заказ №{number} оформлен!

В ближайшее время Вам перезвонит оператор на указанный номер телефона для уточнения деталей заказа
'''
    
def get_ordered_notify_text(order_list: map, number: int, address: str, telephone: str):
    '''
    Текст для отправки уведомления в группу о принятии заказа
    '''
    return f'''
🟡 Поступил заказ №{number}

Номер телефона: <code>{telephone}</code>
Адресс доставки: <i>{address}</i>

{format_cart_list(order_list)}
'''

def get_order_accepted_chat_text(number: int):
    '''
    Текст для принятого заказа в чате
    '''
    return f'🟢 Заказ №{number} принят в обработку'

def get_order_canceled_chat_text(number: int):
    '''
    Текст для принятого заказа в чате
    '''
    return f'🔴 Заказ №{number} отменён'

def get_order_accpeted_client_text(number: int):
    '''
    Текст для принятого заказа (для клиента)
    '''
    return f'''
Ваш заказ №{number} принят!

🚙 Ожидайте доставки и приятного аппетита!
'''

def get_order_canceled_client_text(number: int):
    '''
    Текст для отмененного заказа (для клиента)
    '''
    return f'''
Ваш заказ №{number} отменен по согласованию с оператором
'''

def get_message_hello_edit() -> str:
    '''
    Текст для просмотра сообщения приветствия
    '''
    return f'''
Текст приветствия клиента:

{get_hello_client_text()}

Для установки нового текста отправьте новую версию в ответ на это сообщение.
Нажмите <code>{button_ok}</code> для выхода 
'''

def get_access_restricted_text() -> str:
    '''
    Текст сообщения при блокировке по времени бота
    '''
    return '''
Время для принятия заказов: с 9:00 до 11:00

Попробуйте обратиться позднее
'''

def get_admin_list_text() -> str:
    '''
    Текст для списка администратров
    '''
    return 'Список администраторов'

def get_admin_name() -> str:
    '''
    Текст запроса имени администратора
    '''
    return f'''Напишите имя нового администратора
    
или нажмите кнопку <code>{button_back}</code> для отмены'''

def get_admin_id() -> str:
    '''
    Текст запроса id администратора
    '''
    return f'''Напишите <b>id Telegram профиля</b> администратора

Чтобы его узнать, <b>целевой</b> пользователь должен написать боту <b>IDBot</b> @myidbot в личные сообщения команду <code>/getid</code>

Для отмены создания нажмите на кнопку <code>{button_back}</code>'''

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
        result += f'  {food.name} <i>{food.price} руб.</i> { "" if food.visibility else "🫣" }\n'
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
        if '+' in id_temp:
            ids = id_temp.split('+')
            items = [db.get_item(ids[0]), db.get_item(ids[1])]
            cost = (items[0].price + items[1].price) * count
            summary += cost
            result += f'{counter}. <b>{items[0].name} с {items[1].name}</b> ({items[0].price + items[1].price} руб.) x <b>{count}</b> = {cost} руб.\n\n'
            counter += 1
        else:
            item = db.get_item(id_temp)
            cost = item.price * count
            summary += cost
            result += f'{counter}. <b>{item.name}</b> ({item.price} руб.) x <b>{count}</b> = {cost} руб.\n\n'
            counter += 1
    result += f'Общая сумма заказа: {summary} руб.'
    return result

def format_cart_list_check(cart: map) -> str:
    '''
    Возвращает список товаров из корзины без форматирования для занесения в базу данных
    '''
    if len(cart) == 0:
        return 'Корзина пуста'

    result = ''
    counter = 1
    summary = 0
    for id, count in cart.items():
        id_temp = str(id)
        if '+' in id_temp:
            ids = id_temp.split('+')
            items = [db.get_item(ids[0]), db.get_item(ids[1])]
            cost = (items[0].price + items[1].price) * count
            summary += cost
            result += f'{counter}. {items[0].name} с {items[1].name} ({items[0].price + items[1].price} руб.) x {count} = {cost} руб.\n'
            counter += 1
        else:
            item = db.get_item(id_temp)
            cost = item.price * count
            summary += cost
            result += f'{counter}. {item.name} ({item.price} руб.) x {count} = {cost} руб.\n'
            counter += 1
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
