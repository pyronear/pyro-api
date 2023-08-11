# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import logging
from typing import Optional, Union

import telegram

import app.config as cfg

__all__ = ["resolve_bucket_key", "send_telegram_msg"]

logger = logging.getLogger("uvicorn.warning")


def resolve_bucket_key(file_name: str, bucket_folder: Optional[str] = None) -> str:
    """Prepend file name with bucket subfolder"""
    if not isinstance(bucket_folder, str) and isinstance(cfg.BUCKET_MEDIA_FOLDER, str):
        bucket_folder = cfg.BUCKET_MEDIA_FOLDER

    return f"{bucket_folder}/{file_name}" if isinstance(bucket_folder, str) else file_name


async def send_telegram_msg(
    chat_id: str, text: str, photo: Union[None, str, bytes] = None, test: bool = False
) -> Optional[telegram.Message]:
    """Send telegram message to the chat with the given id

    Args:
        chat_id (str): chat id
        text (str): message to send
        photo (str, bytes or None, default=None): photo to send
        test (bool, default=False): disable notification and delete msg after sending. Used by unittests

    Returns: response
    """
    if not cfg.TELEGRAM_TOKEN:
        logger.warning("Telegram token not set")
        return None
    async with telegram.Bot(cfg.TELEGRAM_TOKEN) as bot:
        try:
            msg: telegram.Message = (
                await bot.send_message(text=text, chat_id=chat_id, disable_notification=test)
                if photo is None
                else await bot.send_photo(chat_id=chat_id, photo=photo, caption=text)
            )
        except telegram.error.TelegramError as e:
            logger.warning(f"Problem sending telegram message to {chat_id}: {e!s}")
        else:
            if test:
                await msg.delete()
            return msg
    return None
