import json
import datetime


def encode_frozenset(o):
    return {
        "_type": "frozenset",
        "value": tuple(o)
    }


def encode_date(o):
    return {
        "_type": "date",
        "year": o.year,
        "month": o.month,
        "day": o.day
    }


def encode_datetime(o):
    return {
        "_type": "datetime",
        "year": o.year,
        "month": o.month,
        "day": o.day,
        "hour": o.hour,
        "minute": o.minute,
        "second": o.second,
        "microsecond": o.microsecond,
        "tzinfo": o.tzinfo
    }


def encode_default(o):
    """
    An encoder for objects that the JSON serializer doesn't recognize.
    """
    if type(o) == frozenset:
        return encode_frozenset(o)
    if type(o) == datetime.date:
        return encode_date(o)
    if type(o) == datetime.datetime:
        return encode_datetime(o)
    return str(o)


def decode_frozenset(o):
    return frozenset(o["value"])


def decode_date(o):
    return datetime.date(o["year"], o["month"], o["day"])


def decode_datetime(o):
    return datetime.datetime(
        o["year"], o["month"], o["day"],
        o["hour"], o["minute"], o["second"], o["microsecond"],
        o["tzinfo"]
    )


def decode_object_hook(o):
    """
    A decoder for objects 
    """
    if o.get("_type") == "frozenset":
        return decode_frozenset(o)
    if o.get("_type") == "date":
        return decode_date(o)
    if o.get("_type") == "datetime":
        return decode_datetime(o)
    return o


def write_lines_deep(file_path, iter):
    """Write a file to filepath, creating directory if necessary"""
    try:
        dirname = path.dirname(file_path)
        makedirs(dirname)
    except:
        pass

    with open(file_path, "w") as f:
        for chunk in iter:
            print(chunk, file=f)


def load_chunks(file_path, object_hook=decode_object_hook):
    """
    Read and parse chunks line by line and return a generator of parsed
    JSON chunks.

    Each line is valid JSON, however, the file as a whole is not valid JSON.
    """
    with open(file_path) as f:
        for chunk in f:
            yield json.loads(chunk, object_hook=object_hook)


def write_chunks(iterable, file_path, default=encode_default):
    """
    Dump an iterable of JSON blobs into a file, line-by-line.

    Each line is valid JSON, however, the file as a whole is not valid JSON.
    """
    write_lines_deep(file_path, (
        json.dumps(chunk, separators=(',', ':'), default=default)
        for chunk in iterable
    ))