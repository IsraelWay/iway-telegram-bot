#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.
from telegram import Update
from telegram.ext import CallbackContext
from mail import mail_service
from pprint import pprint
from time import sleep


def show_state_text(update: Update, context: CallbackContext):
    mail_html = f"<html><body><h1>IsraelWay mail user: {update.effective_user.id}</h1></body></html>"
    # mail_service.send(to="ipolo.box@gmail.com", name="Ilya Polotsky", content=mail_html)
    sleep(10)
    update.message.reply_html(
        f"Привет! Это бот IsraelWay. Переходи на сайт https://israelway.ru, чтобы познакомиться."
        f"{update.effective_user}\n",
        disable_web_page_preview=True)
    return None

