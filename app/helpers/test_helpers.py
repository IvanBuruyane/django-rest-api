import random
import string


def random_string(chars=string.ascii_uppercase + string.digits, n=10):
    return "".join(random.choice(chars) for _ in range(n))
