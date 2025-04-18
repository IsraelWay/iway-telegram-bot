import logging
from logging.handlers import RotatingFileHandler

from telegram import Update
from telegram.ext import Application
from bot.handlers import register_handlers
from settings import Settings


def set_logger():
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

    my_handler = RotatingFileHandler('iway-bot.log', maxBytes=50 * 1024 * 1024, backupCount=2)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)

    app_log = logging.getLogger('root')
    app_log.setLevel(logging.INFO)

    app_log.addHandler(my_handler)


async def post_startup(application):
    await application.bot.send_message(Settings.admin_id(), "Bot started!")
    logging.log(logging.INFO, "Bot started!")


def main():
    set_logger()
    application = Application.builder().token(Settings.bot_token()).post_init(post_startup).build()
    register_handlers(application)
    print("Bot is running")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
