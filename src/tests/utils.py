# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from datetime import datetime
from copy import deepcopy
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def update_only_datetime(entity_as_dict):
    to_return = deepcopy(entity_as_dict)
    if isinstance(to_return.get('created_at'), str):
        to_return["created_at"] = parse_time(to_return["created_at"])
    if isinstance(to_return.get('start_ts'), str):
        to_return["start_ts"] = parse_time(to_return["start_ts"])
    if isinstance(to_return.get('end_ts'), str):
        to_return["end_ts"] = parse_time(to_return["end_ts"])
    return to_return


def parse_time(d):
    return datetime.strptime(d, DATETIME_FORMAT)


def ts_to_string(ts):
    return datetime.strftime(ts, DATETIME_FORMAT)
