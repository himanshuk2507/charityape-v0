import random
import string


class TextGenerator:
    '''
    Handles the generation of a wide range of text types, including encoded strings and one-time passwords
    '''
    def __init__(self, length=None):
        self.length = length or 6

    def otp(self, length=None, selection=string.digits):
        return self.random_string(length, selection)

    @classmethod
    def password_level_string(cls):
        return '{}{}{}'.format(
            string.ascii_letters,
            string.digits,
            string.punctuation
        )

    def random_string(self, length=None, selection=None):
        length = length or self.length
        selection = selection or string.ascii_lowercase
        return ''.join(random.choice(selection) for i in range(length))