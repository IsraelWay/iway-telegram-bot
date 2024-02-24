#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.

from __future__ import print_function
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

from settings import Settings

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = Settings.sendinblue_key()


def send(to, name, content, subject, _tags=None, sender=None, cc=None):
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = subject  # "Hi there! This is IsraelWay."
    html_content = content
    sender = {"name": "IsraelWay Team", "email": "team@israelway.ru"}
    to = [{"email": to, "name": name}]
    bcc = [{"email": "mail-logs@israelway.ru", "name": "mail-logs"}]
    cc = [{"email": cc, "name": "IsraelWay copy"}] if cc else None
    # bcc = [{"name": "John Doe", "email": "example@example.com"}]
    # reply_to = {"email": "replyto@domain.com", "name": "John Doe"}
    # headers = {"Some-Custom-Name": "unique-id-1234"}
    # params = {"parameter": "My param value", "subject": "New Subject"}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject,
                                                   tags=_tags, bcc=bcc, cc=cc)
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
