import hashlib

def hash_digest(s, length=16):
    """
    Given string s, return a hexdigest of `length` (in bits).
    """
    h = hashlib.shake_256(s.encode("utf-8"))
    return h.hexdigest(length)