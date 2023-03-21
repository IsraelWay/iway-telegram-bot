#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from mail import mail_service

from mail.mail_service import render_mail


def show_state_text(update: Update, context: CallbackContext):
    update.message.reply_html(
        f"Привет!\n"
        f"Это бот IsraelWay. Держи нашу <a href='https://bit.ly/iway-deck'>презентацию</a> - "
        f"тут ответы на большинство вопросов, которые, возможно, у тебя возникнут.\n\n"
        f"Если хочешь узнать что-то более подробно, то пиши вот сюда @israelway_IW",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Задать вопрос', url='https://t.me/israelway_IW')],
            [InlineKeyboardButton(text='Наш сайт', url='https://israelway.ru')],
        ]))
    return None

