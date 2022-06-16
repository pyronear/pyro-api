# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import Union


class HTTPRequestException(Exception):
    def __init__(self, status_code: int, response_message: Union[str, None] = None) -> None:
        self.status_code = status_code
        self.response_message = response_message

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, response_message={self.response_message!r})"
