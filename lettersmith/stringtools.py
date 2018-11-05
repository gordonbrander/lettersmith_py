import re


def strip_html(html_str):
    """Remove html tags from a string."""
    return re.sub('<[^<]+?>', '', html_str)


def truncate(text, max_len=250, suffix="..."):
    """
    Truncate a text string to a certain number of characters,
    trimming to the nearest word boundary.
    """
    stripped = strip_html(text).strip()
    if len(stripped) <= max_len:
        return stripped
    substr = stripped[0:max_len + 1]
    words = " ".join(re.split(r"\s+", substr)[0:-1])
    return words + suffix