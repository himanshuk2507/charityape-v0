import string
from itsdangerous import URLSafeTimedSerializer
from flask import request, Blueprint
from skraggle.base_helpers.responser import DataResponse
from skraggle.profile.models import Admin
from skraggle.run import mail
from datetime import datetime
from skraggle.run import app
from skraggle.config import db
from flask_mail import Message

from skraggle.utils.generate_random_string import get_random_string

confirmemail = Blueprint("emailconfirm", __name__, template_folder="templates")


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])


def confirm_token(token, expiration=86400):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=expiration
        )
    except:
        return False
    return email


def eblaster(link, email):
    try:
        msg = Message("Email Confirmation Link", recipients=[email])
        msg.body = link
        msg.html = f"<h1><a href={link}>Click to Confirm your email address</a></h1>"
        mail.send(msg)
        resp = DataResponse(True, "Eblasts Sent Successfully")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:150])
        return resp.status()


def gen_token(email, user):
    token = get_random_string(6, string.digits)
    print(token)
    try:
        msg = Message("[Important!] Confirm your Skraggle account", recipients=[email])
        msg.body = token 
        msg.html = f"<h1>Enter this OTP to confirm your account <strong>{token}</strong></h1>"
        mail.send(msg)
        user.token_reset = token
        db.session.commit()

        print(token)
        return (
            True,
            "An OTP to confirm your email has been sent to your email address.",
        )
    except Exception as e:
        return False, str(e)[:105]


@confirmemail.route("/verification/send", methods=["POST"])
def send_verification_email():
    body = request.json
    admin = Admin.query.filter_by(email=body['email'])
    
    if not admin:
        return DataResponse(False, "User does not exist").status()

    try:
        success, confirmation_response = gen_token(body['email'], admin)
        if not success:
            resp = DataResponse(False, confirmation_response)
            return resp.status()
        return DataResponse(True, confirmation_response).status()
    except Exception as e:
        return DataResponse(False, str(e)).status()


@confirmemail.route("/confirm", methods=["POST"])
def confirm_email():
    try: 
        token = request.json.get('token')
        email = request.json.get('email')
        admin = Admin.query.filter_by(email=email).first()
        if admin.confirmed:
            resp = DataResponse(False, "The Email has already been confirmed")
            return resp.status()
        if not admin.token_reset:
            resp = DataResponse(False, "This OTP has already been used")
            return resp.status()
        if token != admin.token_reset:
            return DataResponse(False, 'This OTP is invalid').status()

        admin.confirmed = True
        admin.confirmed_on = datetime.now()
        admin.token_reset = None
        db.session.commit()
        resp = DataResponse(True, "Your email has been confirmed successfully!")
        return resp.status()
    except Exception:
        resp = DataResponse(False, "This OTP has expired. Please, request for a new verification email")
        return resp.status()
