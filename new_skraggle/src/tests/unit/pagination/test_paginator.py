from src.library.utility_classes.paginator import Paginator


def test_get_query_string():
    """
    Test that get_query_string fetches entire query string from the url string
    """
    url = '127.0.0.1:5000/households?cursor=0&limit=5&direction=after'
    query_component = Paginator.get_query_string(url)
    assert len(query_component) == 32  # the query string in `url` is 32-chars long

    url = '127.0.0.1:5000/households'
    query_component = Paginator.get_query_string(url)
    assert len(query_component) == 0  # the query string in `url` is 0-chars long


def test_parse_query_string():
    """
    Test that parse_query_string fetches keys and values from query string as:

    The result has all of the keys defined in the query string.
    Each key has a corresponding value that equals the value of that key in the query string.
    """
    url = '127.0.0.1:5000/households?cursor=0&limit=5&direction=after&archived=true'
    query_component = Paginator.get_query_string(url)
    data = Paginator.parse_query_string(query_component)
    assert data == {'cursor': '0', 'direction': 'after', 'limit': '5', 'archived': 'true'}

    url = '127.0.0.1:5000/households'
    query_component = Paginator.get_query_string(url)
    data = Paginator.parse_query_string(query_component)
    assert data == {'cursor': None, 'direction': None, 'limit': None, 'archived': None}