import re


class Validator:
    @classmethod
    def is_email(cls, email):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if not re.fullmatch(regex, email):
            return False
        return True