import telebot
from telebot import types

import config
import db
import format

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='HTML')
admin = config.ADMIN_CHAT_ID

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

db.check_database()

@bot.message_handler(commands=['menu', 'меню'])
def edit_menu(message):
    '''
    Выводит список меню администратору для редактирования
    '''
    # Проверка на отправку сообщения из нужного чата
    # print(message.chat.id)
    # print(admin)
    if message.chat.id != admin:
        return
    
    menu = db.get_menu_list()

    if len(menu) == 0:
        bot.send_message(admin, 'Сейчас тут пусто', reply_markup=get_menu_add_keyboard())
    else:
        bot.send_message(admin, format.format_menu_list(menu), reply_markup=get_menu_keyboard())


bot.infinity_polling()
