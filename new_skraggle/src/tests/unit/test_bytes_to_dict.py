from src.library.base_helpers.bytes_to_dict import bytes_to_dict


def test_bytes_to_dict():
    bytes_string = b'{\n  "success": true\n}\n'
    dictionary = bytes_to_dict(bytes_string)
    assert dictionary.get('success') is True
