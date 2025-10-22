#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.

from __future__ import print_function
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

from settings import Settings

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = Settings.sendinblue_key()


def send(to, name, content, subject, _tags=None, sender=None, cc=None, attachments=None):
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = subject  # "Hi there! This is IsraelWay."
    html_content = content
    sender = {"name": "IsraelWay Team", "email": "team@israelway.ru"}
    to = [{"email": to, "name": name}]
    bcc = [{"email": "info@israelway.ru", "name": "IsraelWay Info"}]

    _cc = [{"email": "team@israelway.ru", "name": "IsraelWay team"}]
    try:
        if cc:
            _cc.append({"email": cc, "name": "IsraelWay copy"})
    except Exception as e:
        print("Error on cc in email: %s\n" % e)

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject,
                                                   tags=_tags, bcc=bcc, cc=_cc, attachment=attachments)
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
