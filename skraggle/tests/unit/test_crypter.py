from skraggle.base_helpers.crypter import Crypt

def test_crypter():
    '''
    GIVEN a string A
    WHEN Crypt.encrypt is called 
    AND the returned string B is passed to Crypt.decrypt
    THEN the return value C of Crypt.decrypt is equal to string A
    '''

    crypt = Crypt()
    original_string = "Icheka"
    encrypted_string = crypt.encrypt(original_string)
    decrypted_string = crypt.decrypt(encrypted_string)

    assert decrypted_string == original_string
