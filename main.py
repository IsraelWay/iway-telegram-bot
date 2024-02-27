import threading
import logging
from logging.handlers import RotatingFileHandler

from telegram.ext import Updater

from bot.handlers import register_handlers
from settings import Settings

updater = Updater(token=Settings.bot_token())


def set_logger():
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

    my_handler = RotatingFileHandler('iway-crm.log', maxBytes=50 * 1024 * 1024, backupCount=2)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)

    app_log = logging.getLogger('root')
    app_log.setLevel(logging.INFO)

    app_log.addHandler(my_handler)


def get_updater():
    global updater
    return updater


def main() -> None:
    set_logger()

    dispatcher = updater.dispatcher
    register_handlers(dispatcher)
    # dispatcher.add_handler(conv_handler)
    # dispatcher.add_handler(MessageHandler(Filters.text, show_state_text))
    # dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    updater.bot.send_message(75771603, "Bot started")
    print("Bot is running")
    logging.getLogger('root').info("Bot is running")
    updater.idle()


class FlaskThread(threading.Thread):
    def run(self) -> None:
        from server.server import run_server
        run_server()


if __name__ == '__main__':
    flask_thread = FlaskThread()
    flask_thread.setDaemon(True)
    flask_thread.start()
    main()
