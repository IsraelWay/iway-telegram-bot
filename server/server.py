#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.
import threading

from time import sleep
from flask import Flask, request

from mail import mail_service
from mail.mail_service import render_mail
from main import get_updater
from flask_httpauth import HTTPTokenAuth

from server.iway_responses import DetailedResponse
from settings import Settings
from flask_cors import CORS, cross_origin

c = threading.Condition()

app = Flask("Flask")
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

auth = HTTPTokenAuth(scheme='Bearer')
print("Server is running")


@auth.verify_token
def verify_token(token):
    if token == Settings.auth_token():
        return True


@app.route("/welcome", methods=['POST'])
@auth.login_required
def welcome():
    email, full_name, id_record, preferred_dates = None, None, None, None
    request_data = request.get_json()
    if "email" in request_data:
        email = request_data['email']
    if "full_name" in request_data:
        full_name = request_data['full_name']
    if "id_record" in request_data:
        id_record = request_data['id_record']
    if "preferred_dates" in request_data:
        preferred_dates = request_data['preferred_dates']

    if not email or not full_name:
        return DetailedResponse(result=False, message="Email or full_name are not set",
                                payload=[email, full_name]).__dict__

    mail_html = render_mail(template_name="welcome.html",
                            full_name=full_name,
                            id_record=id_record,
                            first_questions_link=Settings.first_questions_link(),
                            preferred_dates=preferred_dates)

    mail_service.send(to=email, name=full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/anketa", methods=['POST'])
@auth.login_required
def send_anketa():
    email, anketa_link, full_name, id_record = None, None, None, None
    request_data = request.get_json()
    if "email" in request_data:
        email = request_data['email']
    if "anketa_link" in request_data:
        anketa_link = request_data['anketa_link']
    if "full_name" in request_data:
        full_name = request_data['full_name']
    if "id_record" in request_data:
        id_record = request_data['id_record']

    if not email or not anketa_link or not full_name:
        return DetailedResponse(result=False, message="Email/anketa_link/full_name are not set",
                                payload=[email, anketa_link, full_name]).__dict__

    mail_html = render_mail(template_name="anketa.html",
                            full_name=full_name,
                            anketa_link=anketa_link,
                            id_record=id_record)
    mail_service.send(to=email, name=full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route('/')
def hello():
    updater = get_updater()
    c.acquire()
    updater.bot.send_message(75771603, "Запрос на /")
    c.notify_all()
    c.release()
    return 'Welcome to IsraelWay API 1.0'


def run_server():
    app.run(host="0.0.0.0")
