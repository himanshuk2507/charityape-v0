import os

import pyotp
from flask import request, Blueprint, jsonify, render_template, session
from flask_jwt_extended import get_jwt
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

from skraggle.base_helpers.orgGen import getOrg
from skraggle.config import db
from skraggle.base_helpers.responser import DataResponse
from skraggle.decarotor import user_admin_required
from skraggle.profile.models import Admin
from skraggle.run import mail

twofasecurity = Blueprint("twofasecurity", __name__, template_folder="templates")

totp = pyotp.TOTP(os.getenv("SECURITY_PASSWORD_SALT"), interval=120)
# print(verify_otp())


def gen_otp(host_url,name, email):
    try:
        otp = totp.now()
        msg = Message("2FA-Verification", recipients=[email])
        msg.body = "Verify your Login"
        msg.html = (
            f"<p>Hi {name},</p> \r\n Please Verify your Login"
            f"\r\n <p> Your OTP :<strong> {otp} </strong></p>"
            f"Enter the OTP below"
            f"<p>OTP valid only for 2 Minutes </p>"
            f"\r\nor"
            f"\r\nCopy paste the link in your browser to verify"
            f"\r\n {host_url}2fa/verify/{otp}"
        )
        mail.send(msg)
        resp = DataResponse(True, "Eblasts Sent Successfully")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:150])
        return resp.status()


def verify_otp(otp):
    if totp.verify(otp):
        return True
    else:
        return False


@twofasecurity.route("/verify/<otp>", methods=["GET"])
def twofactor_verify(otp):
    if not otp:
        resp = DataResponse(False, "Please Enter The OTP to authenticate")
        return resp.status()
    if verify_otp(otp):
        resp = DataResponse(True, "Authentication Succces")
        session["authenticated"] = True
        session.permanent = True
        return resp.status()
    else:
        resp = DataResponse(
            False, "Failed to Authenticate , Otp Expired or Invalid Try Again"
        )
        return resp.status()


@twofasecurity.route("/<status>", methods=["PATCH"])
@user_admin_required()
def trigger_2fa(status):
    admin = Admin.query.filter_by(
        organization_id=getOrg(get_jwt()), email=get_jwt()["email"]
    ).first()
    if status == "enable":
        print(admin.extra_protection)
        admin.extra_protection = True
    elif status == "disable":
        admin.extra_protection = False
    else:
        resp = DataResponse(False, "Invalid  Parameters: Valid [enable,disable]")
        return resp.status()
    try:
        db.session.commit()
        resp = DataResponse(True, "2 Factor Authentication is {}d".format(status))
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()
