import logging

import requests

from settings import Settings

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000
TELEGRAM_ENDPOINT = f"https://api.telegram.org/bot{Settings.bot_token()}"


def send_telegram_message(chat_id: int, text: str, parse_mode="HTML") -> None:
    url = f"{TELEGRAM_ENDPOINT}/sendMessage"
    logger = logging.getLogger('root')

    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        chunk = text[i:i + MAX_MESSAGE_LENGTH]
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": parse_mode
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Telegram error: {response.text}")
        except Exception as e:
            logger.exception(f"Telegram send failed: {e}")