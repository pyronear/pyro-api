from datetime import datetime
from typing import Any, Dict

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def update_only_datetime(entity_as_dict: Dict[str, Any]):
    return {
        k: parse_time(v) if isinstance(v, str) and k in ("created_at", "start_ts", "end_ts", "last_ping") else v
        for k, v in entity_as_dict.items()
    }


def parse_time(d):
    return datetime.strptime(d, DATETIME_FORMAT)


def ts_to_string(ts):
    return datetime.strftime(ts, DATETIME_FORMAT)
