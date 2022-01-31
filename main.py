from telegram import Update, ParseMode
from telegram.ext import MessageHandler, Updater, Filters, CallbackContext

from handlers.error_handler import error_handler
from settings import Settings


def show_state_text(update: Update, context: CallbackContext):
    update.message.reply_html(
        "Привет! Это бот IsraelWay. Переходи на сайт https://israelway.ru, чтобы познакомиться:\n",
        disable_web_page_preview=True)
    return None


def main() -> None:
    print(Settings.bot_token())
    updater = Updater(token=Settings.bot_token())
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text, show_state_text))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
