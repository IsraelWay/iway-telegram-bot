#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.
import threading

from time import sleep
from flask import Flask

from mail import mail_service
from mail.mail_service import render_mail
from main import get_updater
from flask_httpauth import HTTPTokenAuth

from settings import Settings

c = threading.Condition()

app = Flask("Flask")
auth = HTTPTokenAuth(scheme='Bearer')
print("Server is running")

tokens = {
    "secret-token-1": "airtable",
}


@auth.verify_token
def verify_token(token):
    if token == Settings.auth_token():
        return True


@app.route("/anketa")
@auth.login_required
def send_anketa():
    mail_html = render_mail(template_name="anketa.html",
                            full_name="Красавчик",
                            anketa_link="https://google.com",
                            unsubscribe_link="https://israelway.ru/unsubscribe")
    mail_service.send(to="ipolo.box@gmail.com", name="Ilya Polotsky", content=mail_html)
    return {"result": True, "message": "Email sent successfully"}


@app.route('/')
def hello():
    updater = get_updater()
    c.acquire()
    updater.bot.send_message(75771603, "Запрос на /")
    c.notify_all()
    c.release()
    return 'Welcome to IsraelWay Bot API 1.0'


def run_server():
    app.run(host="0.0.0.0")
