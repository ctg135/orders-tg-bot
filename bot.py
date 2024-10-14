import telebot

import db
import config

bot = telebot.TeleBot(config.BOT_TOKEN)

db.check_database()

bot.infinity_polling()
