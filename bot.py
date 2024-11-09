import datetime
import telebot
import re
from telebot import types

import config
import db
import format

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='HTML')

# Определение глобальных переменных
orders_chat = config.ORDERS_CHAT_ID
admin = config.ADMIN_CHAT_ID

# Корзины пользователей
carts = {}
# Сообщения с корзиной пользователя
cart_message_id = {}
# Проверка базы данных
db.check_database()

def load_admins():
    '''
    Обновляет список администраторов бота
    '''
    global admin
    admin = config.ADMIN_CHAT_ID
    admins = db.get_admins()
    for item in admins:
        admin.append(item[0])

load_admins()

def check_access_time() -> bool:
    '''
    Доступ разрешен в период: с 9:00 до 11:00
    '''
    return True
    now = datetime.datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    if 9 <= current_hour <= 11 and current_minute < 60: return True
    else: return False

def check_access_message(message: types.Message) -> bool:
    '''
    Функция проверки досутпа к сообщениям бота
    Необходима для блокировки бота в нерабочее время
    '''
    access = check_access_time()
    if access: return access
    bot.send_message(message.chat.id, 
                     format.get_access_restricted_text(),
                     reply_markup=format.get_ok_keyboard())
    return access

def check_access_callback(callback: types.CallbackQuery) -> bool:
    '''
    Функция проверки досутпа к callback кнопкам бота
    Необходима для блокировки бота в нерабочее время
    '''
    access = check_access_time()
    if access: return
    bot.delete_message(callback.message.chat.id, callback.message.id)
    bot.send_message(callback.message.chat.id, 
                     format.get_access_restricted_text(),
                     reply_markup=format.get_ok_keyboard())
    return access

@bot.message_handler(commands=['start', 'старт', 'начало'])
def hello_message_command(message):
    '''
    Сообщение приветствия
    '''
    if message.chat.id < 0:  return
    if message.chat.id not in admin:
        # Приветствие пользователя
        if not check_access_message(message):  return
        bot.send_message(message.chat.id, 
                    format.get_hello_client_text(), 
                    reply_markup=format.get_hello_client_keyboard())
    else:
        # Приветствие администратора
        bot.send_message(message.chat.id, 
                     format.get_hello_admin_text(), 
                     reply_markup=format.get_hello_admin_keyboard())

@bot.message_handler(content_types=['text'])
def get_all_mesasge(message):
    '''
    Текстовые сообщения
    '''
    if message.chat.id < 0:  return
    if message.chat.id not in admin:
        if not check_access_message(message):  return
        match message.text:
            case format.button_init_order:
                start_order(message)
            # Приветствие пользователя
            case _: 
                bot.send_message(message.chat.id, 
                    format.get_hello_client_text(), 
                    reply_markup=format.get_hello_client_keyboard())
    else:
        # Обрабтка сообщений главного меню администратора
        match message.text:
            # Вывод меню (полностью)
            case format.button_menu_full:
                menu = db.menu_get_list()
                if len(menu) == 0:
                    bot.send_message(message.chat.id, 'Сейчас тут пусто', reply_markup=format.get_menu_add_keyboard())
                else:
                    bot.send_message(message.chat.id, format.format_menu_list_full(menu), reply_markup=format.get_menu_edit_keyboard())
            # Вывод меню (как для клиента)
            case format.button_menu_nice:
                menu = db.menu_get_list_nice()
                if len(menu) == 0:
                    bot.send_message(message.chat.id, 'Сейчас тут пусто', reply_markup=format.get_menu_add_keyboard())
                else:
                    bot.send_message(message.chat.id, format.format_menu_list_nice(menu), reply_markup=format.get_menu_edit_keyboard())
            # Редактирование текста приветствия клиента
            case format.button_hello_text:
                msg = bot.send_message(message.chat.id, 
                                 format.get_message_hello_edit(),
                                 reply_markup=format.get_ok_keyboard())
                bot.register_next_step_handler(msg, set_hello_message)
            # Редактирование списка администраторов
            case format.button_admins:
                bot.send_message(message.chat.id, 
                                 format.get_admin_list_text(),
                                 reply_markup=format.get_admin_list_edit_keyboard())
            case _:
            # Приветствие администратора
                bot.send_message(message.chat.id, 
                                format.get_hello_admin_text(), 
                                reply_markup=format.get_hello_admin_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def get_callback(callback: types.CallbackQuery):
    # if not check_access_callback(callback):  return
    
    match callback.data:
        # Добавление нового блюда
        case 'menu_add':
            menu_add_item_step1(callback)
            return
        # Редактирование блюда
        case 'menu_edit':
            menu_edit_item_step1(callback)
            return
        # Удаление элемента в меню
        case 'menu_delete':
            menu_delete_item_step1(callback)
            return
    call = callback.data.split('_')
    match call[0]:
        # Редактирование корзины
        case 'cart':
            match call[1]:
                # При удалении
                case 'delete':
                    if '+' in call[2]:
                        carts[callback.message.chat.id].pop(call[2])
                    else: 
                        carts[callback.message.chat.id].pop(int(call[2]))
                    bot.delete_message(callback.message.chat.id, callback.message.id)
                    msg = bot.send_message(callback.message.chat.id,
                        format.format_cart_list(carts[callback.message.chat.id]),
                        reply_markup=format.get_cart_edit_keyboard(carts[callback.message.chat.id])
                        )
                    cart_message_id[callback.message.chat.id] = msg.id
                # При добавлении
                case 'plus':
                    if '+' in call[2]:
                        count = carts[callback.message.chat.id][call[2]]
                        carts[callback.message.chat.id][call[2]] = count + 1
                    else: 
                        count = carts[callback.message.chat.id][int(call[2])]
                        carts[callback.message.chat.id][int(call[2])] = count + 1
                    bot.delete_message(callback.message.chat.id, callback.message.id)
                    msg = bot.send_message(callback.message.chat.id,
                        format.format_cart_list(carts[callback.message.chat.id]),
                        reply_markup=format.get_cart_edit_keyboard(carts[callback.message.chat.id])
                        )
                    cart_message_id[callback.message.chat.id] = msg.id

                # При уменьшении
                case 'minus':
                    if '+' in call[2]:
                        count = carts[callback.message.chat.id][call[2]]
                        if count <= 1:
                            carts[callback.message.chat.id].pop(call[2])
                        else: 
                            carts[callback.message.chat.id][call[2]] = count - 1
                    else: 
                        count = carts[callback.message.chat.id][int(call[2])]
                        if count <= 1:
                            carts[callback.message.chat.id].pop(int(call[2]))
                        else: 
                            carts[callback.message.chat.id][int(call[2])] = count - 1
                    bot.delete_message(callback.message.chat.id, callback.message.id)
                    msg = bot.send_message(callback.message.chat.id,
                        format.format_cart_list(carts[callback.message.chat.id]),
                        reply_markup=format.get_cart_edit_keyboard(carts[callback.message.chat.id])
                        )
                    cart_message_id[callback.message.chat.id] = msg.id
        case 'order':
            # Принятие заказа оператором
            match call[1]:
                case 'accept':
                    client = db.order_accept(int(call[2]))
                    bot.send_message(orders_chat, format.get_order_accepted_chat_text(call[2]))
                    bot.edit_message_reply_markup(callback.message.chat.id, 
                                                  callback.message.id, 
                                                  reply_markup=None)
                    bot.edit_message_text(callback.message.text.replace('🟡', '🟢'), 
                                          callback.message.chat.id, 
                                          callback.message.id)
                    
                    bot.send_message(client,
                                     format.get_order_accpeted_client_text(call[2]),
                                     reply_markup=format.get_hello_client_keyboard())
                    bot.send_sticker(client, 'CAACAgIAAxkBAAENBLxnHRKLdtGhrw1Us1bOPSq8Ohlo_wACHwADDbbSGVMMqpEYFo4gNgQ')
                case 'cancel':
                    client = db.order_cancel(int(call[2]))
                    bot.send_message(orders_chat, format.get_order_canceled_chat_text(call[2]))
                    bot.edit_message_reply_markup(callback.message.chat.id, 
                                                  callback.message.id, 
                                                  reply_markup=None)
                    bot.edit_message_text(callback.message.text.replace('🟡', '🔴'), 
                                          callback.message.chat.id, 
                                          callback.message.id)
                    
                    bot.send_message(client, 
                                     format.get_order_canceled_client_text(call[2]),
                                     reply_markup=format.get_hello_client_keyboard())
        case 'admin':
            bot.delete_message(callback.message.chat.id, 
                               callback.message.id)
            # Редактирование списка администраторов
            match call[1]:
                case 'add':
                    msg = bot.send_message(callback.message.chat.id,
                                           format.get_admin_name(), 
                                           reply_markup=format.get_back_keyboard())
                    bot.register_next_step_handler(callback.message,
                                                   add_admin_step1)
                case 'delete':
                    db.delete_admin(call[2])
                    bot.send_message(callback.message.chat.id, 'Удалено!')
                    bot.send_message(callback.message.chat.id, 
                                 format.get_admin_list_text(),
                                 reply_markup=format.get_admin_list_edit_keyboard())
                    load_admins()


# Секция добавления элемента в меню

def menu_add_item_step1(callback):
    '''
    Определение категории для добавления
    '''
    msg = bot.send_message(callback.message.chat.id, 'Выберите категорию блюда', reply_markup=format.get_menu_category_keyboard())
    bot.register_next_step_handler(msg, menu_add_item_step2)

def menu_add_item_step2(message):
    '''
    Выбор названия
    '''

    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        return

    add_item = db.Food()
    match message.text:
        case format.category_1: add_item.category = 1
        case format.category_2: add_item.category = 2
        case format.category_3: add_item.category = 3
        case format.category_4: add_item.category = 4
        case format.category_5: add_item.category = 5
        case format.button_back: 
            bot.send_message(message.chat.id, 
                     format.get_hello_admin_text(), 
                     reply_markup=format.get_hello_admin_keyboard())
            return
        case _: 
            bot.send_message(message.chat.id, 'Ошибка: неизвестная категория', reply_markup=format.get_hello_admin_keyboard())
            return

    msg = bot.send_message(message.chat.id, 'Введите название', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, menu_add_item_step3, add_item)

def menu_add_item_step3(message, add_item):
    '''
    Выбор цены
    '''

    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        return
    
    add_item.name = message.text
    msg = bot.send_message(message.chat.id, 'Введите цену', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, menu_add_item_step4, add_item)

def menu_add_item_step4(message, add_item):
    '''
    Добавление в меню
    '''

    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите число', reply_markup=format.get_hello_admin_keyboard())
        return
    if not message.text.isdigit():
        bot.send_message(message.chat.id, 'Ошибка: введите число', reply_markup=format.get_hello_admin_keyboard())
        return
    
    add_item.price = message.text
    db.menu_add_item(add_item)
    bot.send_message(message.chat.id, '✅ Готово!', reply_markup=format.get_hello_admin_keyboard())

# Секция редактирования элемента в меню

def menu_edit_item_step1(callback):
    '''
    Предложение категории
    '''
    msg = bot.send_message(callback.message.chat.id, 'Выберите категорию блюда', reply_markup=format.get_menu_category_keyboard())
    bot.register_next_step_handler(msg, menu_edit_item_step2)

def menu_edit_item_step2(message):
    '''
    Выбор категории и предложение номера
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        return
    
    cat = 0
    match message.text:
        case format.category_1: cat = 1
        case format.category_2: cat = 2
        case format.category_3: cat = 3
        case format.category_4: cat = 4
        case format.category_5: cat = 5
        case format.button_back: 
            bot.send_message(message.chat.id, 
                     format.get_hello_admin_text(), 
                     reply_markup=format.get_hello_admin_keyboard())
        case _: 
            bot.send_message(message.chat.id, 'Ошибка: неизвестная категория', reply_markup=format.get_hello_admin_keyboard())
            return
    # Проверка, что выбрана не пустая категория + вывод списка из категории
    menu = db.menu_get_list_category(cat)
    if len(menu) == 0:
        msg = bot.send_message(message.chat.id, 'В этой категории нету блюд', reply_markup=format.get_hello_admin_keyboard())
        return

    msg = bot.send_message(message.chat.id, 
                    f'Выберите блюдо для редактирования:\n{format.format_menu_list_id(menu)}',
                    reply_markup=format.get_menu_id_category_keyboard(menu)) 

    bot.register_next_step_handler(msg, menu_edit_item_step3, menu)

def menu_edit_item_step3(message, menu):
    '''
    Выбор блюда и предложение видимости
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        return
    
    edit_item = None
    for item in menu:
        if str(item.id) == message.text:
            edit_item = item

    if edit_item == None: 
        bot.send_message(message.chat.id, 'Ошибка: укажите корректный номер', reply_markup=format.get_hello_admin_keyboard())
        return
    
    msg = bot.send_message(message.chat.id, 'Укажите видимость в меню', reply_markup=format.get_menu_visibility_edit_keyobard())
    bot.register_next_step_handler(msg, menu_edit_item_step34, edit_item)

def menu_edit_item_step34(message, edit_item):
    '''
    Установка видимости и предложение нового названия
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        return
    
    match message.text:
        case format.button_ok: pass
        case format.button_menu_hidden: edit_item.visibility = 0
        case format.button_menu_visible: edit_item.visibility = 1
        case _: 
            bot.send_message(message.chat.id, 'Ошибка: неизвестный статус', reply_markup=format.get_hello_admin_keyboard())
            return

    msg = bot.send_message(message.chat.id, 'Введите новое название или <i>Ок</i> для продолжения', reply_markup=format.get_ok_keyboard())
    bot.register_next_step_handler(msg, menu_edit_item_step4, edit_item)

def menu_edit_item_step4(message, edit_item):
    '''
    Установка нового названия и предложение новой цены
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        return
    
    if not message.text == 'Ок':
        edit_item.name = message.text

    msg = bot.send_message(message.chat.id, 'Введите новую цену или <i>Ок</i> для продолжения', reply_markup=format.get_ok_keyboard())
    bot.register_next_step_handler(msg, menu_edit_item_step5, edit_item)
    
def menu_edit_item_step5(message, edit_item):
    '''
    Установка новых значений
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите число', reply_markup=format.get_hello_admin_keyboard())
        return
    
    if message.text == 'Ок':
        pass
    elif not message.text.isdigit():
        bot.send_message(message.chat.id, 'Ошибка: введите число', reply_markup=format.get_hello_admin_keyboard())
        return
    else: edit_item.price = message.text

    db.menu_edit_item(edit_item.id, edit_item)
    bot.send_message(message.chat.id, '✅ Готово!', reply_markup=format.get_hello_admin_keyboard())

# Секция удаления элемента в меню

def menu_delete_item_step1(callback):
    '''
    Определение категории для удаления
    '''
    msg = bot.send_message(callback.message.chat.id, 'Выберите категорию блюда', reply_markup=format.get_menu_category_keyboard())
    bot.register_next_step_handler(msg, menu_delete_item_step2)

def menu_delete_item_step2(message):
    '''
    Выбор категории и предложение номера
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        return
    
    cat = 0
    match message.text:
        case format.category_1: cat = 1
        case format.category_2: cat = 2
        case format.category_3: cat = 3
        case format.category_4: cat = 4
        case format.category_5: cat = 5
        case _: 
            bot.send_message(message.chat.id, 'Ошибка: неизвестная категория', reply_markup=format.get_hello_admin_keyboard())
            return

    # Проверка, что выбрана не пустая категория + вывод списка из категории
    menu = db.menu_get_list_category(cat)
    if len(menu) == 0:
        msg = bot.send_message(message.chat.id, 'В этой категории нету блюд', reply_markup=format.get_hello_admin_keyboard())
        return

    msg = bot.send_message(message.chat.id, 
                    f'Выберите блюдо для <b>удаления</b>:\n{format.format_menu_list_id(menu)}',
                    reply_markup=format.get_menu_id_category_keyboard(menu))
    bot.register_next_step_handler(msg, menu_delete_item_step3, menu)

def menu_delete_item_step3(message, menu):
    '''
    Выбор блюда и предложение нового названия
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        return

    food = ''
    for item in menu:
        if str(item.id) == message.text:
            food = item

    if food == '': 
        bot.send_message(message.chat.id, 'Ошибка: укажите корректный номер', reply_markup=format.get_hello_admin_keyboard())
        return

    db.menu_delete_item(food.id)
    bot.send_message(message.chat.id, '✅ Готово!', reply_markup=format.get_hello_admin_keyboard())

# Функция задания нового приветствия для клиента

def set_hello_message(message):
    '''
    Установка нового приветствия для пользователя
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        bot.register_next_step_handler(message, set_hello_message)
        return
    if message.text == format.button_ok:
        get_all_mesasge(message)
        return
    
    db.set_message_hello_text(message.text)

    bot.send_message(message.chat.id, 'Новый текст сообщения установлен!')
    msg = bot.send_message(message.chat.id, 
                                 format.get_message_hello_edit(),
                                 reply_markup=format.get_ok_keyboard())
    bot.register_next_step_handler(msg, set_hello_message)

# Секция добавления администратора 

def add_admin_step1(message: types.Message) -> None:
    '''
    Устанавливает новое имя и запрашивает id администратора
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(add_admin_step1)
        return
    
    if message.text == format.button_back:
        bot.send_message(message.chat.id, 
                     format.get_hello_admin_text(),
                     reply_markup=format.get_hello_admin_keyboard())
        return
    
    msg = bot.send_message(message.chat.id, 
                           format.get_admin_id(), 
                           reply_markup=format.get_back_keyboard())
    bot.register_next_step_handler(msg, add_admin_step2, message.text)

def add_admin_step2(message: types.Message, name: str) -> None:
    '''
    Устанавливает id нового администратора
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(add_admin_step2)
        return

    if message.text == format.button_back:
        bot.send_message(message.chat.id, 
                     format.get_hello_admin_text(),
                     reply_markup=format.get_hello_admin_keyboard())
        return
    
    if not message.text.isdigit():
        bot.send_message(message.chat.id, 'Ошибка: id пользователя - целое положительно число')
        bot.register_next_step_handler(add_admin_step2)
        return
    
    db.add_admin(int(message.text), name)
    bot.send_message(message.chat.id, 'Добавлено!')

    bot.send_message(message.chat.id, 
                     format.get_hello_admin_text(),
                     reply_markup=format.get_hello_admin_keyboard())
    load_admins()


# Секция создания заказа

def start_order(message):
    '''
    Инициация создания заказа
    '''
    if not check_access_message(message):  return
    msg = bot.send_message(message.chat.id, 'Что выберете?', reply_markup=format.get_order_start_keyboard())
    bot.register_next_step_handler(msg, start_order_step2)

def start_order_step2(message):
    '''
    Обработка кнопок меню пользователя
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        start_order(message)
        return

    global carts
    if message.chat.id not in carts.keys():
        carts.update({message.chat.id: {}})

    match message.text:
        case format.button_back:
            if message.chat.id in carts.keys():
                carts.pop(message.chat.id)
            hello_message_command(message)
        case format.category_1:
            order_food_simple_step1(message, 1)
        case format.category_2:
            order_food_simple_step1(message, 2)
        case format.category_3:
            order_food_simple_step1(message, 3)
        case format.category_4:
            order_food_simple_step1(message, 4)
        case format.category_6:
            order_food_simple_step1(message, 6)
        case format.button_cart:
            cart_edit_step1(message)
        case format.button_make_order:
            make_order(message)
        case _: 
            msg = bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
            bot.register_next_step_handler(msg, start_order_step2)

def order_food_simple_step1(message, category):
    '''
    Функция для добавления в заказ простых блюд
    Выгружает выбранную категории и показывает выбор пользователю
    '''
    if not check_access_message(message):  return
    menu = db.menu_get_list_category_nice(category)
    msg = bot.send_message(message.chat.id, 
                     format.format_menu_list_nice(menu),
                     reply_markup=format.get_menu_keyboard(menu))
    bot.register_next_step_handler(msg, order_food_simple_step2, menu, category)

def order_food_simple_step2(message, menu, category):
    '''
    Проверяет введенное название и предлагает выбрать количество
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        start_order(message)
        return
    if message.text == format.button_back:
        start_order(message)
        return
    id = format.get_id_from_name(menu, message.text)
    if id == -1:
        bot.send_message(message.chat.id, format.message_no_menu)
        start_order(message)
        return
    msg = bot.send_message(message.chat.id, 'Сколько добавить?', reply_markup=format.get_numbers_keyboard())
    bot.register_next_step_handler(msg, order_food_simple_step3, id, category)

def order_food_simple_step3(message, id, category):
    '''
    Проверка введенного числа и добавление в корзину
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(message, order_food_simple_step3, id, category)
        return
    if message.text == format.button_back:
        order_food_simple_step1(message, category)
        return
    if not message.text.isdigit():
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(message, order_food_simple_step3, id, category)
        return
    count = 0
    try:
        count = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(message, order_food_simple_step3, id, category)
        return
    if count <= 0:
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(message, order_food_simple_step3, id, category)
        return
    
    global carts
    if id in carts[message.chat.id].keys():
        carts[message.chat.id][id] += count
    else:
        carts[message.chat.id][id] = count
    
    bot.send_message(message.chat.id, 'Добавлено')
    bot.send_message(message.chat.id, 'Что-нибдуь ещё?')
    order_food_simple_step1(message, category)
    
def order_food_complex_step1(message, category):
    '''
    Функция для добавления в заказ сложных блюд
    Выгружает первую часть подкатегории позиции (гарнир)
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        start_order(message)
        return
    
    menu = []
    if category == 2:
        menu = db.menu_get_list_category_nice(category)
    else: 
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        start_order(message)
        return
    
    if len(menu) == 0:
        bot.send_message(message.chat.id, format.get_menu_no_items_text())
        start_order(message)
        return
    
    msg = bot.send_message(message.chat.id, 
                     format.format_menu_list_nice(menu),
                     reply_markup=format.get_menu_keyboard(menu))
    bot.register_next_step_handler(msg, order_food_complex_step2, menu, category)
    
def order_food_complex_step2(message, menu, category):
    '''
    Установка первой выбранной части и предложение второй
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        start_order(message)
        return
    if message.text == format.button_back:
        start_order(message)
        return
    
    id = format.get_id_from_name(menu, message.text)
    if id == -1:
        bot.send_message(message.chat.id, format.get_menu_no_items_text())
        start_order(message)
        return
    
    menu = []
    if category == 2:
        menu = db.menu_get_list_category_nice(category + 1)
    else: 
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        start_order(message)
        return
    
    if len(menu) == 0:
        bot.send_message(message.chat.id, format.get_menu_no_items_text())
        start_order(message)
        return
    msg = bot.send_message(message.chat.id, 
                     format.format_menu_list_nice(menu),
                     reply_markup=format.get_menu_keyboard(menu))
    bot.register_next_step_handler(message, order_food_complex_step3, menu, category, id)

def order_food_complex_step3(message, menu, category, first_id):
    '''
    Установка второй части и предложение количества
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        order_food_complex_step1(message)
        return
    if message.text == format.button_back:
        order_food_complex_step1(message)
        return
    
    second_id = format.get_id_from_name(menu, message.text)
    if second_id == -1:
        bot.send_message(message.chat.id, format.get_menu_no_items_text())
        order_food_complex_step1(message)
        return
    msg = bot.send_message(message.chat.id, 
                           'Сколько добавить?', 
                           reply_markup=format.get_numbers_keyboard())
    bot.register_next_step_handler(msg, order_food_complex_step4, menu, category, first_id, second_id)

def order_food_complex_step4(message, menu, category, first_id, second_id):
    '''
    Установка количества
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(message, order_food_complex_step4, id, category)
        return
    if message.text == format.button_back:
        order_food_simple_step1(message, category)
        return
    if not message.text.isdigit():
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(message, order_food_complex_step4, id, category)
        return
    count = 0
    try:
        count = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
    
        bot.register_next_step_handler(message, order_food_complex_step4, id, category)
        return
    if count <= 0:
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(message, order_food_complex_step4, id, category)
        return
    
    id = f'{first_id}+{second_id}'
    global carts
    if id in carts[message.chat.id].keys():
        carts[message.chat.id][id] += count
    else:
        carts[message.chat.id][id] = count
    
    bot.send_message(message.chat.id, 'Добавлено')
    bot.send_message(message.chat.id, 'Что-нибдуь ещё?')
    order_food_complex_step1(message, category)

# Секция редактирования корзины

def cart_edit_step1(message):
    '''
    Отправка списка выбранных товаров и меню для его редактирования
    Список товаров с ценником и количеством и итогом
    Кнопки на сообщении:
        Товар - [delete]
        [+] [-] [Количество]
    '''
    if not check_access_message(message):  return
    global carts
    msg = bot.send_message(message.chat.id, 
                           format.get_cart_help_text(), 
                           reply_markup=format.get_cart_keyboard())
    msg_cart = bot.send_message(message.chat.id,
                     format.format_cart_list(carts[message.chat.id]),
                     reply_markup=format.get_cart_edit_keyboard(carts[message.chat.id])
                     )
    cart_message_id[message.chat.id] = msg_cart.id
    bot.register_next_step_handler(msg, cart_edit_step2)

def cart_edit_step2(message):
    '''
    Обработка текстовых кнопок пользователя в меню корзины
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(msg, cart_edit_step2)
        return

    # Удаление сообщения с корзиной перед обработкой заказа
    if message.chat.id in cart_message_id.keys():
        bot.delete_message(message.chat.id, cart_message_id.pop(message.chat.id))
    
    match message.text:
        case format.button_back:
            start_order(message)
        case format.button_cart_clear:
            carts[message.chat.id] = {}
            bot.send_message(message.chat.id, 'Корзина очищена')
            start_order(message)
        case format.button_make_order:
            make_order(message)
        case _:
            msg = bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
            bot.register_next_step_handler(msg, cart_edit_step2)

# Секция обработки заказа

def make_order(message):
    '''
    Начинает обработку заказа
    Если корзина пустая, то возвращает.
    В другом случае спрашиваем: номер телефона (если нету в базе);
    Адрес доставки (если нету в базе)
    И отправляем в чат для заказов предложение принять/отменить
    '''
    if not check_access_message(message):  return
    global carts
    if message.chat.id not in carts.keys() or carts[message.chat.id] == {}:
        msg = bot.send_message(message.chat.id, format.get_cart_empty_text())
        start_order(msg)
        return
    
    # Удаление сообщения с корзиной перед обработкой заказа
    if message.chat.id in cart_message_id.keys():
        bot.delete_message(message.chat.id, cart_message_id.pop(message.chat.id))
        
    
    bot.send_message(message.chat.id, 
                     format.get_order_ok_text(carts[message.chat.id]),
                     reply_markup=format.get_order_ok_keyboard()
                     )
    bot.register_next_step_handler(message, make_order_step1)

def make_order_step1(message):
    '''
    Подтверждает выбор пользователя и предлагает номер телефона
    Также предлагает ввести старый номер телефона
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        start_order(message)
        return
    if message.text == format.button_back:
        start_order(message)
        return

    match message.text:
        case format.button_ok:
            telephone = db.get_telephone_from_last_order(message.chat.id)
            msg = bot.send_message(message.chat.id,
                             format.get_order_telephone_text(telephone),
                             reply_markup=format.get_order_telephone_keyboard(telephone))
            bot.register_next_step_handler(msg, make_order_step2)
        case '_':
            start_order(message)
            return
            
def make_order_step2(message):
    '''
    Получает номер телефона и предлагает ввести адрес
    Также предлагает ввести адрес из предыдущего заказа
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(message, make_order_step2)
        return
    if message.text == format.button_back:
        start_order(message)
        return
    
    telepgone_regexp = r'(\s*)?(\+)?([- _():=+]?\d[- _():=+]?){10,14}(\s*)?'
    match = re.match(telepgone_regexp, message.text)

    if not match:
        bot.send_message(message.chat.id, 'Ошибка: некорректный номер телефона')
        bot.register_next_step_handler(message, make_order_step2)
        return

    address = db.get_address_from_last_order(message.chat.id)

    msg = bot.send_message(message.chat.id,
                           format.get_order_address_text(address),
                           reply_markup=format.get_order_address_keyboard(address))
    bot.register_next_step_handler(msg, make_order_step3, match.string)
    
def make_order_step3(message, telephone):
    '''
    Получает адрес и отправляет сообщение в группу
    '''
    if not check_access_message(message):  return
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(message, make_order_step3)
        return
    if message.text == format.button_back:
        message.text = format.button_ok
        make_order_step1(message)
        return
    if '\"' in message.text or '\'' in message.text:
        bot.send_message(message.chat.id, 'Ошибка: некорректный адрес')
        bot.register_next_step_handler(message, make_order_step3)
        return
    
    number = db.order_add(message.chat.id, 
                 telephone, 
                 message.text, 
                 format.format_cart_list_check(carts[message.chat.id]))

    bot.send_message(message.chat.id,
                     format.get_ordered_user_text(number),
                     reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(orders_chat,
                     format.get_ordered_notify_text(carts.pop(message.chat.id), 
                                                    number,
                                                    message.text,
                                                    telephone),
                     reply_markup=format.get_ordered_accept_keyboard(number))


bot.infinity_polling()

