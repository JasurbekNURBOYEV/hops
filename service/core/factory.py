"""
This is a bot factory module which is roughly used to create full bot instance
"""
# IMPORTS
# built-in
# local
# django-specific
from django.conf import settings

# other/external
import telebot


# initialize a bot instance
bot = telebot.TeleBot(token=settings.BOT_TOKEN)


# --- START: definition of bot instance

@bot.message_handler(commands=['start'])
def start(message):
    text = message.text
    if text == '/start':
        bot.reply_to(message, 'Hello from the other side')


# --- END: definition of bot instance
