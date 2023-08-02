# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import logging
from time import sleep
from typing import Optional

import requests
from requests import Response

import app.config as cfg

__all__ = ["resolve_bucket_key", "send_telegram_msg"]

logger = logging.getLogger("uvicorn.warning")


def resolve_bucket_key(file_name: str, bucket_folder: Optional[str] = None) -> str:
    """Prepend file name with bucket subfolder"""
    if not isinstance(bucket_folder, str) and isinstance(cfg.BUCKET_MEDIA_FOLDER, str):
        bucket_folder = cfg.BUCKET_MEDIA_FOLDER

    return f"{bucket_folder}/{file_name}" if isinstance(bucket_folder, str) else file_name


def send_telegram_msg(chat_id: str, message: str, autodelete: bool = False) -> Optional[Response]:
    """Send telegram message to the chat with the given id

    Args:
        chat_id (str): chat id
        message (str): message to send
        autodelete (str): delete msg after sending. Used for tests

    Returns: response
    """
    if not cfg.TELEGRAM_TOKEN:
        logger.warning("Telegram token not set")
        return None
    base_url = f"https://api.telegram.org/bot{cfg.TELEGRAM_TOKEN}"
    response = requests.get(f"{base_url}/sendMessage?chat_id={chat_id}&text={message}", timeout=5)
    if response.status_code != 200 or "ok" not in response.json() or not response.json()["ok"]:
        logger.warning(f"Problem sending telegram message to {chat_id}: {response.status_code, response.text}")
    elif autodelete:
        sleep(5)
        try:
            msg_id = response.json()["result"]["message_id"]
            del_response = requests.get(f"{base_url}/deleteMessage?chat_id={chat_id}&message_id={msg_id}", timeout=5)
            assert del_response.status_code == 200
        except Exception as e:
            logger.warning(f"Could not delete telegram msg: {e}")
    return response
