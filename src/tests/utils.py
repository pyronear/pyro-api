import datetime as datetime
from copy import deepcopy
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def update_only_datetime(entity_as_dict):
    to_return = deepcopy(entity_as_dict)
    if "created_at" in to_return:
        to_return["created_at"] = parse_time(to_return["created_at"])
    return to_return


def parse_time(d):
    return datetime.strptime(d, DATETIME_FORMAT)
