#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.

class AirtableRequest:
    def __init__(self, request, required_fields=None):
        request_data = request.get_json()
        if "email" in request_data:
            self.email = request_data['email']
        else:
            raise Exception("No required param email")

        if "full_name" in request_data:
            self.full_name = request_data['full_name']
        else:
            raise Exception("No required param full_name")

        if "id_record" in request_data:
            self.id_record = request_data['id_record']
        else:
            raise Exception("No required param id_record")

        if "tg_id" in request_data:
            self.tg_id = request_data['tg_id']
        else:
            raise Exception("No required param tg_id")

        if "email_html" in request_data:
            self.email_html = request_data['email_html']
        elif "email_html" in required_fields:
            raise Exception("No required param email_html")

        if "invitation_url" in request_data:
            self.invitation_url = request_data['invitation_url']
        elif "invitation_url" in required_fields:
            raise Exception("No required param invitation_url")

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

        if "email_picture" in request_data:
            self.email_picture = request_data['email_picture']
        elif "email_picture" in required_fields:
            raise Exception("No required param email_picture")

        if "fill_agreement_url" in request_data:
            self.fill_agreement_url = request_data['fill_agreement_url']
        elif "fill_agreement_url" in required_fields:
            raise Exception("No required param fill_agreement_url")

        if "preferred_dates" in request_data:
            self.preferred_dates = request_data['preferred_dates']
        elif "preferred_dates" in required_fields:
            raise Exception("No required param preferred_dates")
