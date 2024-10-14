import telebot
from telebot import types

import config
import db
import format

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='HTML')
admin = config.ADMIN_CHAT_ID

db.check_database()

@bot.message_handler(commands=['start', 'старт', 'начало'])
def start_admin(message):
    '''
    Сообщение приветствия администратора
    '''
    if message.chat.id not in admin:
        return
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
        bot.send_message(message.chat.id, format.format_menu_list(menu), reply_markup=format.get_menu_keyboard())

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
            pass

# Секция добавления элемента в меню

add_item = db.Food()
def menu_add_item_step1(callback):
    '''
    Определение категории
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

    global add_item
    match message.text:
        case format.category_1: add_item.category = 1
        case format.category_2: add_item.category = 2
        case format.category_3: add_item.category = 3
        case format.category_4: add_item.category = 4
        case _: 
            bot.send_message(message.chat.id, 'Ошибка: неизвестная категория', reply_markup=format.get_hello_admin_keyboard())
            return

    msg = bot.send_message(message.chat.id, 'Введите название', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, menu_add_item_step3)

def menu_add_item_step3(message):
    '''
    Выбор цены
    '''

    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        return
    
    global add_item
    add_item.name = message.text
    msg = bot.send_message(message.chat.id, 'Введите цену', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, menu_add_item_step4)

def menu_add_item_step4(message):
    '''
    Добавление в меню
    '''

    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите число', reply_markup=format.get_hello_admin_keyboard())
        return
    if not message.text.isdigit():
        bot.send_message(message.chat.id, 'Ошибка: введите число', reply_markup=format.get_hello_admin_keyboard())
        return
    
    global add_item
    add_item.price = message.text
    db.menu_add_item(add_item)
    bot.send_message(message.chat.id, '✅ Готово!', reply_markup=format.get_hello_admin_keyboard())

# Секция редактирования элемента в меню

edit_item = db.Food()
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
        case _: 
            bot.send_message(message.chat.id, 'Ошибка: неизвестная категория', reply_markup=format.get_hello_admin_keyboard())
            return
    # Проверка, что выбрал не пустую категорию
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
    
    
    msg = bot.send_message(message.chat.id, 'Введите новое название или <i>Ок</i> для продолжения', reply_markup=format.get_ok_keyboard())
    bot.register_next_step_handler(msg, menu_edit_item_step4, food)

def menu_edit_item_step4(message, food):
    '''
    Установка нового название и предложение новой цены
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите текст', reply_markup=format.get_hello_admin_keyboard())
        return
    global edit_item
    if message.text == 'Ок': edit_item.name = food.name
    else: edit_item.name = message.text

    msg = bot.send_message(message.chat.id, 'Введите новую цену или <i>Ок</i> для продолжения', reply_markup=format.get_ok_keyboard())
    bot.register_next_step_handler(msg, menu_edit_item_step5, food)
    
def menu_edit_item_step5(message, food):
    '''
    Установка новых значений
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: введите число', reply_markup=format.get_hello_admin_keyboard())
        return
    global edit_item
    if message.text == 'Ок':
        edit_item.price = food.price
    elif not message.text.isdigit():
        bot.send_message(message.chat.id, 'Ошибка: введите число', reply_markup=format.get_hello_admin_keyboard())
        return
    else: edit_item.price = message.text

    db.menu_edit_item(food.id, edit_item)
    bot.send_message(message.chat.id, '✅ Готово!', reply_markup=format.get_hello_admin_keyboard())


bot.infinity_polling()
