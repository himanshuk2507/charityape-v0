import random
import string

def get_random_string(length = 8, string_type = string.ascii_lowercase):
    # choose from all lowercase letter
    letters = string_type
    return ''.join(random.choice(letters) for i in range(length))