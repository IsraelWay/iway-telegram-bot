import os


class Settings:

    IS_TEST = True

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

    @staticmethod
    def first_questions_link() -> str:
        return "https://web.miniextensions.com/YknIZlIqVswRiGObohd4/" if Settings.IS_TEST else "https://web.miniextensions.com/YknIZlIqVswRiGObohd4/"

    @staticmethod
    def details_form() -> str:
        return "https://web.miniextensions.com/b2kiZbC976kwEuizeeHY" if Settings.IS_TEST else "https://web.miniextensions.com/b2kiZbC976kwEuizeeHY"

    @staticmethod
    def masa_form() -> str:
        return "https://web.miniextensions.com/K3pC5QWCpRHcntwO6n63" if Settings.IS_TEST else "https://web.miniextensions.com/K3pC5QWCpRHcntwO6n63"


if Settings.IS_TEST:
    print("Test environment")
