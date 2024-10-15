import datetime
import telebot
from telebot import types

import config
import db
import format

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='HTML')
admin = config.ADMIN_CHAT_ID
basket = {}

db.check_database()

@bot.message_handler(commands=['start', 'старт', 'начало'])
def hello_message_command(message):
    '''
    Сообщение приветствия
    '''
    if message.chat.id not in admin:
        # Приветствие пользователя
        now = datetime.datetime.now()
        bot.send_message(message.chat.id, 
                    format.get_hello_client_text(), 
                    reply_markup=format.get_hello_client_keyboard())
        if (now.time().hour > 11):
            bot.send_message(message.chat.id, 
                    format.get_hello_client_late_text())
    else:
        # Приветствие администратора
        bot.send_message(message.chat.id, 
                     format.get_hello_admin_text(), 
                     reply_markup=format.get_hello_admin_keyboard())

@bot.message_handler(commands=['menu', 'меню'])
def list_menu(message):
    '''
    Выводит список меню администратору для редактирования
    '''
    if message.chat.id not in admin:
        return
    
    menu = db.menu_get_list()

    if len(menu) == 0:
        bot.send_message(message.chat.id, 'Сейчас тут пусто', reply_markup=format.get_menu_add_keyboard())
    else:
        bot.send_message(message.chat.id, format.format_menu_list_full(menu), reply_markup=format.get_menu_keyboard())

@bot.message_handler(content_types=['text'])
def get_all_mesasge(message):
    '''
    Текстовые сообщения
    '''
    if message.chat.id not in admin:
        match message.text:
            case format.button_init_order:
                start_order(message)
            # Приветствие пользователя
            case _: 
                bot.send_message(message.chat.id, 
                    format.get_hello_client_text(), 
                    reply_markup=format.get_hello_client_keyboard())
                if datetime.datetime.now().time().hour >= 11:
                    bot.send_message(message.chat.id, 
                        format.get_hello_client_late_text())
    else:
        # Обрабтка сообщений главного меню администратора
        match message.text:
            case format.button_menu_full:
                menu = db.menu_get_list()
                if len(menu) == 0:
                    bot.send_message(message.chat.id, 'Сейчас тут пусто', reply_markup=format.get_menu_add_keyboard())
                else:
                    bot.send_message(message.chat.id, format.format_menu_list_full(menu), reply_markup=format.get_menu_keyboard())
            case format.button_menu_nice:
                menu = db.menu_get_list_nice()
                if len(menu) == 0:
                    bot.send_message(message.chat.id, 'Сейчас тут пусто', reply_markup=format.get_menu_add_keyboard())
                else:
                    bot.send_message(message.chat.id, format.format_menu_list_nice(menu), reply_markup=format.get_menu_keyboard())
            case _:
            # Приветствие администратора
                bot.send_message(message.chat.id, 
                                format.get_hello_admin_text(), 
                                reply_markup=format.get_hello_admin_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def get_callback(callback):
    match callback.data:
        # Добавление нового блюда
        case 'menu_add':
            menu_add_item_step1(callback)
        # Редактирование блюда
        case 'menu_edit':
            menu_edit_item_step1(callback)
        # Удаление элемента в меню
        case 'menu_delete':
            menu_delete_item_step1(callback)

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

# Секция создания заказа

def start_order(message):
    '''
    Инициация создания заказа
    '''
    msg = bot.send_message(message.chat.id, 'Что выберете?', reply_markup=format.get_order_start_keyboard())
    bot.register_next_step_handler(msg, start_order_step2)

def start_order_step2(message):
    '''
    Обработка кнопок меню пользователя
    '''
    match message.text:
        case format.button_back:
            hello_message_command(message)
            # TODO Сброс корзины
        case format.button_category_1:
            order_food_simple(message, 1)
        case format.button_category_2:
            pass
        case format.button_category_3:
            order_food_simple(message, 4)
        case format.button_category_4:
            order_food_simple(message, 5)
        case format.button_basket:
            pass
        case format.button_make_order:
            pass
        case _: 
            msg = bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
            bot.register_next_step_handler(msg, start_order_step2)

def order_food_simple(message, category):
    '''
    Функция для добавления в заказ простых блюд
    Выгружает выбранную категории и показывает выбор пользователю
    '''
    menu = db.menu_get_list_category_nice(category)
    # TODO: сделать клавиатуру для названий позиций
    bot.send_message(message.chat.id, format.format_menu_list_nice(menu))




bot.infinity_polling()
