from itsdangerous import json


def byte_to_dict(byte_str):
    return json.loads(byte_str.decode('utf-8'))