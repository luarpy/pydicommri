import random
import string

def random_str(**lenght: int) -> str:
    if lenght:
        k = lenght
    else:
        k = 8
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=k))

def random_int(a: int, b: int = None) -> int:
    if b is None:
        a, b = 0, a
    return random.randint(a, b)