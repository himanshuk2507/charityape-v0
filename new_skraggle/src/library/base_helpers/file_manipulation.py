from pathlib import Path
from re import findall
from os import path, getcwd
from requests import get as get_request, head as fetch_headers
from ntpath import basename, split as split_path

from src.library.utility_classes.text_generator import TextGenerator


def download_file(url: str = None):
    '''
    Download the file at the `url` and return a path to the downloaded file.
    :param url: Location of file to download.
    :returns str | None
    '''
    if url is None:
        return None
    try:
        if not is_downloadable(url):
            return None
        req = get_request(url, allow_redirects=True)
        file_name = get_filename_from_content_disposition(req.headers.get('content-disposition'))\
            or TextGenerator(length=16).random_string()
        file_path = Path(getcwd())/file_name
        open(path, 'wb').write(req.content)
        return file_path
    except Exception as e:
        print(str(e))
        return None


def get_filename_from_content_disposition(disposition: str = None):
    if not disposition:
        return None
    filenames = findall('filename=(.+)', disposition)
    return filenames[0] if len(filenames) != 0 else None


def is_downloadable(url: str = None):
    if url is None:
        return False
    try:
        req = fetch_headers(url, allow_redirects=True)
        content_type = req.headers.get('content-type')
        for unallowed in ['text', 'html']:
            if unallowed in content_type.lower():
                return False
        return True
    except Exception as e:
        print(str(e))
        return False

    
def get_filename_from_path(file_path: str = None):
    if file_path is None:
        return None

    head, tail = split_path(file_path)
    return tail or basename(head)