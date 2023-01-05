from itsdangerous import json


def bytes_to_dict(byte_str):
    '''
    Converts a bytes-string to a Python dictionary.
    '''
    return json.loads(byte_str.decode('utf-8'))