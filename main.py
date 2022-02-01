import threading

from telegram.ext import MessageHandler, Updater, Filters
from handlers.error_handler import error_handler
from handlers.state_handlers import show_state_text
from settings import Settings

updater = Updater(token=Settings.bot_token())


def get_updater():
    global updater
    return updater


def main() -> None:
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text, show_state_text))
    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    print("Bot is running")
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

