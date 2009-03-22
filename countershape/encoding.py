
ENCODING = "utf-8"

class binary(str): pass

def encode(o):
    if isinstance(o, binary):
        return o
    else:
        u = unicode(o)
        return u.encode("utf-8")

