from skraggle.utils.generate_random_string import get_random_string


def test_get_random_string_1():
    '''
    GIVEN a call to get_random_string
    WHEN the function invocation contains 0 arguments
    THEN an 8-character string is returned
    '''
    
    string = get_random_string()
    assert len(string) == 8


def test_get_random_string_2():
    '''
    GIVEN a call to get_random_string
    WHEN the function invocation contains 1 argument and this argument is an integer L
    THEN a string of length L is returned
    '''
    
    L = 10
    string = get_random_string(L)
    assert len(string) == L