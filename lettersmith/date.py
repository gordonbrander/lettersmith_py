from datetime import date, datetime
from os import path


def read_file_times(pathlike):
    """
    Given a pathlike, return a tuple of `(created_time, modified_time)`.
    Both return values are datetime objects.

    If no value can be found, will return unix epoch for both.
    """
    try:
        modified_time = date.fromtimestamp(path.getmtime(pathlike))
        created_time = date.fromtimestamp(path.getctime(pathlike))
        return created_time, modified_time
    except OSError:
        return EPOCH, EPOCH


def parse_iso_8601(dt_str):
    """
    Parse an ISO 8601 date string into a datetime. Supports the following date
    styles:

    2017-01-01
    20170101
    2017 01 01
    """
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d").date()
    except ValueError:
        pass
    try:
        return datetime.strptime(dt_str, "%Y%m%d").date()
    except ValueError:
        pass
    return datetime.strptime(dt_str, "%Y %m %d").date()


def format_iso_8601(date):
    """
    Format datetime as ISO 8601 https://en.wikipedia.org/wiki/ISO_8601
    '%Y-%m-%d'
    """
    return date.isoformat()


EPOCH = date.fromtimestamp(0)
EPOCH_ISO_8601 = format_iso_8601(EPOCH)