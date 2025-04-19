#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.
import logging


class AirtableRequest:
    def __init__(self, request, required_fields=None, exclude_fields=None):
        if required_fields is None:
            required_fields = []
        if exclude_fields is None:
            exclude_fields = []
        request_data = request.get_json()

        # required
        if "email" in request_data:
            self.email = request_data['email']
        elif "email" not in exclude_fields:
            raise Exception("No required param email")

        if "full_name" in request_data:
            self.full_name = request_data['full_name']
        elif "full_name" not in exclude_fields:
            raise Exception("No required param full_name")

        if "id_record" in request_data:
            self.id_record = request_data['id_record']
        elif "id_record" not in exclude_fields:
            raise Exception("No required param id_record")

        if "tg_id" in request_data:
            self.tg_id = request_data['tg_id']
        elif "tg_id" not in exclude_fields:
            raise Exception("No required param tg_id")

        # not required

        # needed for common ===============================
        if "email_html" in request_data:
            self.email_html = request_data['email_html']
        elif "email_html" in required_fields:
            raise Exception("No required param email_html")

        try:
            self.email_picture = request_data["email_picture"]
        except:
            self.email_picture = "https://thumb.tildacdn.com/tild3033-6631-4636-b931-313031666332/-/format/webp/Screenshot_2023-12-2.png"

        # if "email_picture" in request_data:
        #     self.email_picture = request_data['email_picture']
        # elif "email_picture" in required_fields:
        #     raise Exception("No required param email_picture")

        if "actions" in request_data:
            self.actions = request_data['actions']
        elif "actions" in required_fields:
            raise Exception("No required param actions")

        if "attachments" in request_data:
            self.attachments = request_data['attachments']
        elif "attachments" in required_fields:
            raise Exception("No required param attachments")

        if "main_title" in request_data:
            self.main_title = request_data['main_title']
        elif "main_title" in required_fields:
            raise Exception("No required param main_title")

        if "subject" in request_data:
            self.subject = request_data['subject']
        elif "subject" in required_fields:
            raise Exception("No required param subject")

        if "cc" in request_data:
            self.cc = request_data['cc']
        elif "cc" in required_fields:
            raise Exception("No required param cc")
        else:
            self.cc = request_data.get('cc')
        # ===================================================

        if "invitation_url" in request_data:
            self.invitation_url = request_data['invitation_url']
        elif "invitation_url" in required_fields:
            raise Exception("No required param invitation_url")

        if "support_action" in request_data:
            self.support_action = request_data['support_action']
        elif "support_action" in required_fields:
            raise Exception("No required param support_action")

        if "target" in request_data:
            self.target = request_data['target']
        elif "target" in required_fields:
            raise Exception("No required param target")

        if "consul_info" in request_data:
            self.consul_info = request_data['consul_info']
        elif "consul_info" in required_fields:
            raise Exception("No required param consul_info")

        if "report_ua_url" in request_data:
            self.report_ua_url = request_data['report_ua_url']
        elif "report_ua_url" in required_fields:
            raise Exception("No required param report_ua_url")

        if "agreement_text_url" in request_data:
            self.agreement_text_url = request_data['agreement_text_url']
        elif "agreement_text_url" in required_fields:
            raise Exception("No required param agreement_text_url")

        if "fill_agreement_url" in request_data:
            self.fill_agreement_url = request_data['fill_agreement_url']
        elif "fill_agreement_url" in required_fields:
            raise Exception("No required param fill_agreement_url")

        if "preferred_dates" in request_data:
            self.preferred_dates = request_data['preferred_dates']
        elif "preferred_dates" in required_fields:
            raise Exception("No required param preferred_dates")

        if "anketa_id" in request_data:
            self.anketa_id = request_data['anketa_id']
        elif "anketa_id" in required_fields:
            raise Exception("No required param anketa_id")

        if "avia_dates" in request_data:
            self.avia_dates = request_data['avia_dates']
        elif "avia_dates" in required_fields:
            raise Exception("No required param avia_dates")

        if "reasons" in request_data:
            self.reasons = request_data['reasons']
        elif "reasons" in required_fields:
            raise Exception("No required param reasons")

        if "is_passed" in request_data:
            self.is_passed = request_data['is_passed']
        elif "is_passed" in required_fields:
            raise Exception("No required param is_passed")

        if "anketa_zalog_url" in request_data:
            self.anketa_zalog_url = request_data['anketa_zalog_url']
        elif "anketa_zalog_url" in required_fields:
            raise Exception("No required param anketa_zalog_url")
