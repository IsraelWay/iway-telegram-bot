import os

from flask.cli import load_dotenv
load_dotenv(".env")


class Settings:

    IS_TEST = True

    @staticmethod
    def airtable_api_key():
        try:
            from_env = os.environ[f"AIRTABLE_API_KEY{'_TEST' if Settings.IS_TEST else ''}"]
        except KeyError:
            from_env = None
        return from_env if from_env else None

    @staticmethod
    def airtable_leads_table_id():
        try:
            from_env = os.environ[f"AIRTABLE_LEADS_TABLE_ID{'_TEST' if Settings.IS_TEST else ''}"]
        except KeyError:
            from_env = None
        return from_env if from_env else "tblUyPrVrDu4k2O8w"
    
    @staticmethod
    def airtable_programs_template_table_id():
        try:
            from_env = os.environ[f"AIRTABLE_PROGRAMS_TEMPLATE_TABLE_ID{'_TEST' if Settings.IS_TEST else ''}"]
        except KeyError:
            from_env = None
        return from_env if from_env else "tblNnMW6ABLUZjyZV"

    @staticmethod
    def airtable_base_id():
        try:
            from_env = os.environ[f"AIRTABLE_BASE_ID{'_TEST' if Settings.IS_TEST else ''}"]
        except KeyError:
            from_env = None
        return from_env if from_env else "app4VDqwiDMUFRPt9"

    @staticmethod
    def admin_id():
        try:
            from_env = os.environ[f"ADMIN_ID{'_TEST' if Settings.IS_TEST else ''}"]
        except KeyError:
            from_env = None
        return from_env if from_env else 75771603

    @staticmethod
    def bot_token():
        return os.environ[f"BOT_TOKEN{'_TEST' if Settings.IS_TEST else ''}"]

    @staticmethod
    def sendinblue_key():
        return os.environ[f"SENDINBLUE_KEY{'_TEST' if Settings.IS_TEST else ''}"]

    @staticmethod
    def auth_token():
        return os.environ[f"AUTH_TOKEN{'_TEST' if Settings.IS_TEST else ''}"]

    @staticmethod
    def bot_name() -> str:
        return "masa_israelway_bot" if Settings.IS_TEST else "test_masa_israelway_bot"

    # @staticmethod
    # def first_questions_link() -> str:
    #     return "https://web.miniextensions.com/YknIZlIqVswRiGObohd4" if Settings.IS_TEST else "https://web.miniextensions.com/YknIZlIqVswRiGObohd4"

    # @staticmethod
    # def details_form() -> str:
    #     return "https://web.miniextensions.com/b2kiZbC976kwEuizeeHY" if Settings.IS_TEST else "https://web.miniextensions.com/b2kiZbC976kwEuizeeHY"

    # @staticmethod
    # def masa_form() -> str:
    #     return "https://web.miniextensions.com/K3pC5QWCpRHcntwO6n63" if Settings.IS_TEST else "https://web.miniextensions.com/K3pC5QWCpRHcntwO6n63"

    # @staticmethod
    # def consul_date_form() -> str:
    #     return "https://web.miniextensions.com/YA4sDCqK6QN1dMY8lmXR" if Settings.IS_TEST else "https://web.miniextensions.com/YA4sDCqK6QN1dMY8lmXR"

    # @staticmethod
    # def consul_confirm_form() -> str:
    #     return "https://web.miniextensions.com/YbxdaJAnYvG0aOFOItrX" if Settings.IS_TEST else "https://web.miniextensions.com/YbxdaJAnYvG0aOFOItrX"

    # @staticmethod
    # def upload_agreement_form() -> str:
    #     return "https://web.miniextensions.com/vdYsbDSHBZGidRbb5aaA" if Settings.IS_TEST else "https://web.miniextensions.com/vdYsbDSHBZGidRbb5aaA"

    # @staticmethod
    # def upload_medblank_form() -> str:
    #     return "https://web.miniextensions.com/lSmisfMfnBBOfplBrjgv" if Settings.IS_TEST else "https://web.miniextensions.com/lSmisfMfnBBOfplBrjgv"

    # @staticmethod
    # def upload_payment_form() -> str:
    #     return "https://web.miniextensions.com/6QtBryI3eBFdSa89y7Z8" if Settings.IS_TEST else "https://web.miniextensions.com/6QtBryI3eBFdSa89y7Z8"

    # @staticmethod
    # def upload_tickets_form() -> str:
    #     return "https://web.miniextensions.com/LeU0ZnqOM8OPiCWB9Oaf" if Settings.IS_TEST else "https://web.miniextensions.com/LeU0ZnqOM8OPiCWB9Oaf"

    # @staticmethod
    # def onward_docs_form() -> str:
    #     return "https://web.miniextensions.com/mCByUtmBSVv0Im6oP7im" if Settings.IS_TEST else "https://web.miniextensions.com/mCByUtmBSVv0Im6oP7im"

    # @staticmethod
    # def living_form() -> str:
    #     return "https://web.miniextensions.com/sOJUBmwhl5dYaz9U1Zri" if Settings.IS_TEST else "https://web.miniextensions.com/sOJUBmwhl5dYaz9U1Zri"


if Settings.IS_TEST:
    print("Test environment")
