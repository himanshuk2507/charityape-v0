import os

DEFAULT_PAGE_SIZE = 5
RELEASE_LEVEL = os.environ["RELEASE_LEVEL"]

def get_base_url():
    local = 'http://127.0.0.1:5000'
    stage = 'http://18.212.161.170.nip.io:5100'
    prod = ''

    if not RELEASE_LEVEL:
        return local
    if RELEASE_LEVEL == 'stage':
        return stage
    return prod

BASE_URL = get_base_url()