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
    def bot_name() -> str:
        return "masa_israelway_bot" if Settings.IS_TEST else "test_masa_israelway_bot"


if Settings.IS_TEST:
    print("Test environment")
