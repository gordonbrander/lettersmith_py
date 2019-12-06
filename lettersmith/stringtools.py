import re


_FIRST_SENTENCE = r'^[^.]+'


def first_sentence(plain_text):
    """
    Get the first sentence in a block of plain text.
    Does not include period at end of sentence.
    """
    match = re.match(_FIRST_SENTENCE, plain_text)
    if match:
        return match.group(0)
    else:
        return ""


def truncate(text, max_len=250, suffix="..."):
    """
    Truncate a text string to a certain number of characters,
    trimming to the nearest word boundary.
    """
    stripped = text.strip()
    if len(stripped) <= max_len:
        return stripped
    substr = stripped[0:max_len + 1]
    words = " ".join(re.split(r"\s+", substr)[0:-1])
    return words + suffix