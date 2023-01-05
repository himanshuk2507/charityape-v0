from os import getcwd
from pathlib import Path
import rsa


def private_key_from_string(key: str = None):
    if not key:
        raise Exception('private_key_from_string() requires `key` to be a valid RSA key')
    key = key.strip().split(', ')
    return rsa.PrivateKey(
        n=int(key[0]),
        e=int(key[1]),
        d=int(key[2]),
        p=int(key[3]),
        q=int(key[4]),
    )


def private_key_from_file(file_path: str = None):
    if not file_path:
        raise Exception('private_key_from_file() requires `file_path`')
    try:
        return private_key_from_string(open(file_path, 'r').readline().strip())
    except Exception as e:
        print(e)
        return None


def public_key_from_string(key: str = None):
    if not key:
        raise Exception('public_key_from_string() requires `key` to be a valid RSA key')
    
    key = key.strip().split(', ')
    
    return rsa.PublicKey(
        n=int(key[0]),
        e=int(key[1])
    )


def stripe_secret_private_key(organization_id: str = None):
    if not organization_id:
        raise Exception('stripe_secret_private_key() requires `organization_id`')
    return private_key_from_file(
        Path(getcwd())/'enc'/'stripe'/organization_id
    )
    

def paypal_client_secret_private_key(organization_id: str = None):
    if not organization_id:
        raise Exception('paypal_secret_private_key() requires `organization_id`')
    return private_key_from_file(
        Path(getcwd())/'enc'/'paypal'/'cl_secret{}'.format(organization_id)
    )
    

def paypal_client_id_private_key(organization_id: str = None):
    if not organization_id:
        raise Exception('paypal_client_id_private_key() requires `organization_id`')
    return private_key_from_file(
        Path(getcwd())/'enc'/'paypal'/'cl_id{}'.format(organization_id)
    )
    

def eventbrite_private_key(organization_id: str = None):
    if not organization_id:
        raise Exception('eventbrite_private_key() requires `organization_id`')
    return private_key_from_file(
        Path(getcwd())/'enc'/'eventbrite'/'oauth_key{}'.format(organization_id)
    )


def decrypt_rsa(encrypted: str = None, private_key: rsa.PrivateKey = None):
    if not encrypted or not private_key:
        raise Exception('decrypt_rsa() requires `encrypted` and `private_key`')
    try:
        return rsa.decrypt(encrypted, private_key).decode()
    except rsa.DecryptionError as e:
        print(str(e))
        return None