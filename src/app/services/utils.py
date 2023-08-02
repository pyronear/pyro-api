# Copyright (C) 2020-2023, Pyronear.
# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Optional

import requests
from fastapi import HTTPException, status

import app.config as cfg

__all__ = ["resolve_bucket_key", "send_telegram_msg"]


def resolve_bucket_key(file_name: str, bucket_folder: Optional[str] = None) -> str:
    """Prepend file name with bucket subfolder"""
    if not isinstance(bucket_folder, str) and isinstance(cfg.BUCKET_MEDIA_FOLDER, str):
        bucket_folder = cfg.BUCKET_MEDIA_FOLDER

    return f"{bucket_folder}/{file_name}" if isinstance(bucket_folder, str) else file_name


def send_telegram_msg(chat_id: str, message: str) -> None:
    """Send telegram message to the chat with the given id. Raise HTTPException if it fails

    Args:
        chat_id (str): chat id
        message (str): message to send
    """
    if not cfg.TELEGRAM_TOKEN:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Telegram token not set")
    url = f"https://api.telegram.org/bot{cfg.TELEGRAM_TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    response = requests.get(url)
    if response.status_code != 200 or "ok" not in response.json() or not response.json()["ok"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Problem sending telegram message: {response.status_code, response.text}",
        )
