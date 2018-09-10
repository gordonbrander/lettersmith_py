from datetime import date, datetime
from os import path
from functools import singledispatch


def read_file_times(pathlike):
    """
    Given a pathlike, return a tuple of `(created_time, modified_time)`.
    Both return values are datetime objects.

    If no value can be found, will return unix epoch for both.
    """
    path_str = str(pathlike)
    try:
        modified_time = datetime.fromtimestamp(path.getmtime(path_str))
        created_time = datetime.fromtimestamp(path.getctime(path_str))
        return created_time, modified_time
    except OSError:
        return EPOCH, EPOCH


@singledispatch
def to_datetime(x):
    """
    Given a date or datetime, return a datetime.
    Used to read datetime values from meta fields.
    """
    raise TypeError("read function not implemented for type {}".format(type(x)))


@to_datetime.register(datetime)
def datetime_to_datetime(dt):
    return dt


@to_datetime.register(date)
def date_to_datetime(d):
    """
    Convert a date to a datetime.
    """
    return datetime(d.year, d.month, d.day)


@to_datetime.register(str)
def date_to_datetime(s):
    """
    Convert an ISO 8601 date string to a datetime.
    """
    return parse_isoformat(s)


def parse_isoformat(dt_str):
    """
    Parse an ISO 8601 date string into a datetime. Supports the following date
    styles:

    2017-01-01
    20170101
    2017 01 01
    """
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d")
    except ValueError:
        pass
    try:
        return datetime.strptime(dt_str, "%Y%m%d")
    except ValueError:
        pass
    return datetime.strptime(dt_str, "%Y %m %d")


def format_isoformat(dt):
    """
    Format datetime as ISO 8601 https://en.wikipedia.org/wiki/ISO_8601
    '%Y-%m-%d'
    """
    return dt.date().isoformat()


EPOCH = datetime.fromtimestamp(0)
EPOCH_ISO_8601 = format_isoformat(EPOCH)
