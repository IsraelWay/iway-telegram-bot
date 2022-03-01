#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.
from telegram import Update
from telegram.ext import CallbackContext
from mail import mail_service

from mail.mail_service import render_mail


def show_state_text(update: Update, context: CallbackContext):
    update.message.reply_html(
        f"Привет! Это бот IsraelWay. Переходи на сайт https://israelway.ru, чтобы познакомиться.",
        disable_web_page_preview=True)
    return None

