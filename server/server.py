#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.
import threading
from pprint import pprint

from time import sleep
from flask import Flask, request

from mail import mail_service
from mail.mail_service import render_mail
from main import get_updater
from flask_httpauth import HTTPTokenAuth

from server.iway_requests import AirtableRequest
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
    email, full_name, id_record, preferred_dates, email_html = None, None, None, None, None
    request_data = request.get_json()
    if "email" in request_data:
        email = request_data['email']
    if "full_name" in request_data:
        full_name = request_data['full_name']
    if "id_record" in request_data:
        id_record = request_data['id_record']
    if "preferred_dates" in request_data:
        preferred_dates = request_data['preferred_dates']
    if "email_html" in request_data:
        email_html = request_data['email_html']

    if not email or not full_name:
        return DetailedResponse(result=False, message="Email or full_name are not set",
                                payload=[email, full_name]).__dict__

    mail_html = render_mail(template_name="welcome.html",
                            full_name=full_name,
                            id_record=id_record,
                            email_html=email_html,
                            first_questions_link=Settings.first_questions_link(),
                            preferred_dates=preferred_dates)

    mail_service.send(to=email, name=full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/anketa/masa", methods=['POST'])
@auth.login_required
def send_anketa():
    email, full_name, id_record, id_form_record, email_html = None, None, None, None, None
    request_data = request.get_json()
    if "email" in request_data:
        email = request_data['email']
    if "full_name" in request_data:
        full_name = request_data['full_name']
    if "id_record" in request_data:
        id_record = request_data['id_record']
    if "id_form_record" in request_data:
        id_form_record = request_data['id_form_record']
    if "email_html" in request_data:
        email_html = request_data['email_html']

    if not email or not full_name:
        return DetailedResponse(result=False, message="Email or full_name are not set",
                                payload=[email, full_name]).__dict__

    anketa_link = Settings.masa_form() + "/" + id_form_record

    mail_html = render_mail(template_name="anketa.html",
                            full_name=full_name,
                            anketa_link=anketa_link,
                            email_html=email_html,
                            id_record=id_record)
    mail_service.send(to=email, name=full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/plan", methods=['POST'])
@auth.login_required
def send_plan():
    email, target, full_name, id_record, email_html = None, None, None, None, None
    request_data = request.get_json()
    if "email" in request_data:
        email = request_data['email']
    if "target" in request_data:
        target = request_data['target']
    if "full_name" in request_data:
        full_name = request_data['full_name']
    if "id_record" in request_data:
        id_record = request_data['id_record']
    if "email_html" in request_data:
        email_html = request_data['email_html']

    if not email or not target or not full_name:
        return DetailedResponse(result=False, message="Email / target / full_name are not set",
                                payload=[email, target, full_name]).__dict__

    mail_html = render_mail(
        template_name="plan.html",
        full_name=full_name,
        id_record=id_record,
        email_html=email_html,
        details_form_link=Settings.details_form())
    mail_service.send(to=email, name=full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/invitation-letter", methods=['POST'])
@auth.login_required
def invitation_letter():
    try:
        air_request = AirtableRequest(request, ["invitation_url", "email_html", "consul_info"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="invitation-letter.html",
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=air_request.email_html,
        consul_date_form_url=Settings.consul_date_form(),
        consul_info=air_request.consul_info,
        invitation_url=air_request.invitation_url,
        consul_confirm_form_url=Settings.consul_confirm_form()
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/report-ua", methods=['POST'])
@auth.login_required
def send_report_ua():
    try:
        air_request = AirtableRequest(request, ["report_ua_url", "email_html"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="report-ua.html",
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=air_request.email_html,
        report_ua_url=air_request.report_ua_url,
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/hook", methods=['POST'])
def hook():
    pprint(request.files)
    pprint(request.form)
    pprint(request.json)
    pprint(request.query_string)
    pprint(request.data)
    return "sone"


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
