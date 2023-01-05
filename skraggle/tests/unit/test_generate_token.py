
from skraggle.profile.email_confirmation import confirm_token, generate_confirmation_token


email = 'my-email@test.com'

def test_gen_token():
    token = generate_confirmation_token(email)
    assert confirm_token(token) == email