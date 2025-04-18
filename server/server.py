#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.
import json
from logging.handlers import RotatingFileHandler

import markdown
import logging

from pprint import pprint

from time import sleep

import requests
from flask import Flask, request

from mail import mail_service
from mail.mail_service import render_mail
from flask_httpauth import HTTPTokenAuth

from iway_requests import AirtableRequest
from iway_responses import DetailedResponse
from settings import Settings
from flask_cors import CORS

MAX_MESSAGE_LENGTH = 4000


def send_telegram_message(chat_id: int, text: str, parse_mode="HTML") -> None:
    url = f"https://api.telegram.org/bot{Settings.bot_token()}/sendMessage"
    logger = logging.getLogger('root')

    # разбиваем текст по частям
    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        chunk = text[i:i + MAX_MESSAGE_LENGTH]
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": parse_mode
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Telegram error: {response.text}")
        except Exception as e:
            logger.exception(f"Telegram send failed: {e}")


def set_logger():
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

    my_handler = RotatingFileHandler('iway-api.log', maxBytes=50 * 1024 * 1024, backupCount=2)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)

    app_log = logging.getLogger('root')
    app_log.setLevel(logging.INFO)

    app_log.addHandler(my_handler)


#
# Start
#
app = Flask("Flask")
CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

auth = HTTPTokenAuth(scheme='Bearer', header='Authorization')
print("Server is running")


@app.before_request
def before_request_func():
    req_data = {'endpoint': request.endpoint, 'method': request.method, 'cookies': request.cookies,
                'headers': dict(request.headers)}
    req_data['headers'].pop('Cookie', None)
    req_data['args'] = request.args
    req_data['form'] = request.form
    req_data['remote_addr'] = request.remote_addr
    send_telegram_message(
        Settings.admin_id(), "Server request: " + json.dumps(req_data, indent=4))

    req_data['data'] = request.data.decode("utf-8")
    logging.getLogger('root').info("/ request " + json.dumps(req_data, indent=4))


@auth.verify_token
def verify_token(token):
    try:
        schema, token = request.headers.get('Authorization', '').split(None, 1)
        return token == Settings.auth_token()
    except ValueError:
        return False


@app.route("/welcome", methods=['POST'])
@auth.login_required
def welcome():
    try:
        air_request = AirtableRequest(request, ["email_html", "preferred_dates"])
        logging.getLogger('root').info("Welcome email to " + air_request.email)
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(template_name="welcome.html",
                            full_name=air_request.full_name,
                            id_record=air_request.id_record,
                            email_html=air_request.email_html,
                            first_questions_link=Settings.first_questions_link(),
                            preferred_dates=air_request.preferred_dates)

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/anketa/masa", methods=['POST'])
@auth.login_required
def send_anketa():
    try:
        air_request = AirtableRequest(request, ["email_html", "anketa_id"])
        logging.getLogger('root').info("Anketa to " + air_request.email)

    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    anketa_link = Settings.masa_form() + "/" + air_request.anketa_id
    mail_html = render_mail(template_name="anketa.html",
                            full_name=air_request.full_name,
                            anketa_link=anketa_link,
                            email_html=air_request.email_html,
                            id_record=air_request.id_record)
    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/plan", methods=['POST'])
@auth.login_required
def send_plan():
    try:
        air_request = AirtableRequest(request, ["target", "email_html"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="plan.html",
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=air_request.email_html,
        details_form_link=Settings.details_form())
    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
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


@app.route("/agreement", methods=['POST'])
@auth.login_required
def agreement():
    try:
        air_request = AirtableRequest(request, ["email_picture", "agreement_text_url", "fill_agreement_url"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="agreement.html",
        email_picture=air_request.email_picture,
        agreement_text_url=air_request.agreement_text_url,
        fill_agreement_url=air_request.fill_agreement_url,
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=air_request.email_html,
        upload_agreement_form=Settings.upload_agreement_form()
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/medblank", methods=['POST'])
@auth.login_required
def medblank():
    try:
        air_request = AirtableRequest(request, ["email_picture"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="medblank.html",
        email_picture=air_request.email_picture,
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=air_request.email_html,
        upload_medblank_url=Settings.upload_medblank_form()
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/anketa/zalogs", methods=['POST'])
@auth.login_required
def anketa_zalogs():
    try:
        air_request = AirtableRequest(request, ["email_html", "anketa_zalog_url"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="anketa_zalog.html",
        anketa_zalog_url=air_request.anketa_zalog_url,
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=air_request.email_html
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/payment-email", methods=['POST'])
@auth.login_required
def payment_email():
    try:
        air_request = AirtableRequest(request, ["email_html", "email_picture"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="payment.html",
        email_picture=air_request.email_picture,
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=air_request.email_html,
        upload_payment_url=Settings.upload_payment_form()
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/avia-dates", methods=['POST'])
@auth.login_required
def avia_dates():
    try:
        air_request = AirtableRequest(request, ["avia_dates"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="avia-dates.html",
        email_picture=air_request.email_picture,
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=air_request.email_html,
        avia_dates=air_request.avia_dates,
        upload_tickets_url=Settings.upload_tickets_form(),
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/living-request", methods=['POST'])
@auth.login_required
def living_request():
    try:
        air_request = AirtableRequest(request)
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="living.html",
        email_picture=air_request.email_picture,
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=air_request.email_html,
        living_form_url=Settings.living_form(),
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/support-action", methods=['POST'])
@auth.login_required
def support_action():
    try:
        air_request = AirtableRequest(request, ["support_action"], ["id_record"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="support-action.html",
        support_action=air_request.support_action,
        email_picture=air_request.email_picture,
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=markdown.markdown(air_request.email_html),
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/onward-check-results", methods=['POST'])
@auth.login_required
def onward_check_results():
    try:
        air_request = AirtableRequest(request, ["reasons", "is_passed"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="onward-check-results.html",
        email_picture=air_request.email_picture,
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        is_passed=air_request.is_passed,
        email_html=air_request.email_html,
        reasons=air_request.reasons,
        onward_docs_url=Settings.onward_docs_form(),
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/onward-docs", methods=['POST'])
@auth.login_required
def onward_docs():
    try:
        air_request = AirtableRequest(request, ["email_html", "email_picture"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="onward-docs.html",
        email_picture=air_request.email_picture,
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        email_html=air_request.email_html,
        onward_docs_url=Settings.onward_docs_form(),
    )

    mail_service.send(to=air_request.email, name=air_request.full_name, content=mail_html)
    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/send-email", methods=['POST'])
@auth.login_required
def send_email():
    try:
        air_request = AirtableRequest(request, ["email_html", "email_picture", "actions", "main_title", "subject"])
    except Exception as e:
        return DetailedResponse(result=False, message=str(e),
                                payload=request.get_json()).__dict__

    mail_html = render_mail(
        template_name="common.html",
        email_html=air_request.email_html,
        email_picture=air_request.email_picture,
        full_name=air_request.full_name,
        id_record=air_request.id_record,
        actions=air_request.actions,
        main_title=air_request.main_title
    )

    mail_service.send(to=air_request.email, cc=air_request.cc if air_request.cc else None,
                      subject=air_request.subject if air_request.subject else "IsraelWay team",
                      name=air_request.full_name, content=mail_html)

    return DetailedResponse(result=True, message="Email sent successfully").__dict__


@app.route("/hook", methods=['POST'])
def hook():
    pprint(request.files)
    pprint(request.form)
    pprint(request.json)
    pprint(request.query_string)
    pprint(request.data)
    return "sone"


@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200


@app.route('/')
def hello():
    return 'Welcome to IsraelWay API 1.0'


if __name__ == '__main__':
    set_logger()
    logging.log(logging.INFO, "Starting server... iw logger is running")
    app.run(debug=True, host='0.0.0.0', port=5000)
