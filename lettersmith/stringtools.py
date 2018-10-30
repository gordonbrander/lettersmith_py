import re


def strip_html(html_str):
    """Remove html tags from a string."""
    return re.sub('<[^<]+?>', '', html_str)


def truncate(text, max_len=250, suffix="..."):
    """
    Truncate a text string to a certain number of characters,
    trimming to the nearest word boundary.
    """
    trimmed = text.strip()
    if len(trimmed) < max_len:
        return trimmed
    elif re.match("\s", trimmed[max_len]):
        return re.sub("\s+$", "", trimmed[0:max_len]) + suffix
    else:
        return re.sub("\s+\S+?$", "", trimmed[0:max_len]) + suffix