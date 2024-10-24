import datetime
import telebot
from telebot import types

import config
import db
import format

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='HTML')
admin = config.ADMIN_CHAT_ID

# Корзины пользователей
carts = {}

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
        bot.send_message(message.chat.id, format.format_menu_list_full(menu), reply_markup=format.get_menu_edit_keyboard())

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
                    bot.send_message(message.chat.id, format.format_menu_list_full(menu), reply_markup=format.get_menu_edit_keyboard())
            case format.button_menu_nice:
                menu = db.menu_get_list_nice()
                if len(menu) == 0:
                    bot.send_message(message.chat.id, 'Сейчас тут пусто', reply_markup=format.get_menu_add_keyboard())
                else:
                    bot.send_message(message.chat.id, format.format_menu_list_nice(menu), reply_markup=format.get_menu_edit_keyboard())
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
                    bot.send_message(callback.message.chat.id,
                        format.format_cart_list(carts[callback.message.chat.id]),
                        reply_markup=format.get_cart_edit_keyboard(carts[callback.message.chat.id])
                        )
                # При добавлении
                case 'plus':
                    if '+' in call[2]:
                        count = carts[callback.message.chat.id][call[2]]
                        carts[callback.message.chat.id][call[2]] = count + 1
                    else: 
                        count = carts[callback.message.chat.id][int(call[2])]
                        carts[callback.message.chat.id][int(call[2])] = count + 1
                    bot.delete_message(callback.message.chat.id, callback.message.id)
                    bot.send_message(callback.message.chat.id,
                        format.format_cart_list(carts[callback.message.chat.id]),
                        reply_markup=format.get_cart_edit_keyboard(carts[callback.message.chat.id])
                        )
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
                    bot.send_message(callback.message.chat.id,
                        format.format_cart_list(carts[callback.message.chat.id]),
                        reply_markup=format.get_cart_edit_keyboard(carts[callback.message.chat.id])
                        )

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
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        start_order(message)
        return

    global carts
    if message.chat.id not in carts.keys():
        carts.update({message.chat.id: {}})

    match message.text:
        case format.button_back:
            hello_message_command(message)
            # TODO Сброс корзины
        case format.button_category_1:
            order_food_simple_step1(message, 1)
        case format.button_category_2:
            order_food_complex_step1(message, 2)
        case format.button_category_3:
            order_food_simple_step1(message, 4)
        case format.button_category_4:
            order_food_simple_step1(message, 5)
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
    menu = db.menu_get_list_category_nice(category)
    msg = bot.send_message(message.chat.id, 
                     format.format_menu_list_nice(menu),
                     reply_markup=format.get_menu_keyboard(menu))
    bot.register_next_step_handler(msg, order_food_simple_step2, menu, category)

def order_food_simple_step2(message, menu, category):
    '''
    Проверяет введенное название и предлагает выбрать количество
    '''
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
    global carts
    msg = bot.send_message(message.chat.id, 
                           format.get_cart_help_text(), 
                           reply_markup=format.get_cart_keyboard())
    bot.send_message(message.chat.id,
                     format.format_cart_list(carts[message.chat.id]),
                     reply_markup=format.get_cart_edit_keyboard(carts[message.chat.id])
                     )
    

    bot.register_next_step_handler(msg, cart_edit_step2)
    # Отправка второго сообщения

def cart_edit_step2(message):
    '''
    Обработка текстовых кнопок пользователя в меню корзины
    '''
    if not message.content_type == 'text':
        bot.send_message(message.chat.id, 'Ошибка: неизвестная команда')
        bot.register_next_step_handler(msg, cart_edit_step2)
        return

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
    '''
    pass


bot.infinity_polling()

