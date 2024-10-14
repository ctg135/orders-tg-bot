import telebot
from telebot import types

import config
import db
import format

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='HTML')
admin = config.ADMIN_CHAT_ID

db.check_database()

@bot.message_handler(commands=['menu', 'меню'])
def list_menu(message):
    '''
    Выводит список меню администратору для редактирования
    '''
    # Проверка на отправку сообщения из нужного чата
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
        case 'menu_add':
            menu_add_item_step1(callback)
        case 'menu_edit':
            # Редактирование элемента в меню
            pass
        case 'menu_delete':
            # Удаление элемента в меню
            pass

add_item = db.Food()
# TODO Добавить проверку, что отправлен только текст

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
    global add_item
    match message.text:
        case format.category_1: add_item.category = 1
        case format.category_2: add_item.category = 2
        case format.category_3: add_item.category = 3
        case format.category_4: add_item.category = 4
    msg = bot.send_message(message.chat.id, 'Введите название', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, menu_add_item_step3)

def menu_add_item_step3(message):
    '''
    Выбор цены
    '''
    global add_item
    add_item.name = message.text
    msg = bot.send_message(message.chat.id, 'Введите цену', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, menu_add_item_step4)

def menu_add_item_step4(message):
    '''
    Добавление в меню
    '''
    global add_item
    add_item.price = message.text
    db.menu_add_item(add_item)
    bot.send_message(message.chat.id, 'Готово!', reply_markup=types.ReplyKeyboardRemove())



bot.infinity_polling()
