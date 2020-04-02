import telebot

from conf import config


# u need to write to bot first to give him access
_bot = telebot.TeleBot(config.TELEGRAM_TOKEN)
_bot_important = telebot.TeleBot(config.IMPORTANT_TELEGRAM_TOKEN)
_admin = config.TELEGRAM_ADMIN


def online_log(text):
    _bot.send_message(_admin, text, parse_mode='Markdown')


def online_log_important(text):
    _bot_important.send_message(_admin, text, parse_mode='Markdown')
