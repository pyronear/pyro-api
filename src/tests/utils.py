from copy import deepcopy
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def update_only_datetime(entity_as_dict):
    to_return = deepcopy(entity_as_dict)
    for key in ("created_at", "start_ts", "end_ts", "last_ping"):
        if isinstance(to_return.get(key), str):
            to_return[key] = parse_time(to_return[key])
    return to_return


def parse_time(d):
    return datetime.strptime(d, DATETIME_FORMAT)


def ts_to_string(ts):
    return datetime.strftime(ts, DATETIME_FORMAT)
