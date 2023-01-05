from flask import Response

from src.library.base_helpers.bytes_to_dict import bytes_to_dict

def assert_is_ok(response: Response = None):
    data = bytes_to_dict(response.data)
    
    assert response.status_code == 200
    assert data.get('success') is True