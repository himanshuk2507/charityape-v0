from datetime import datetime, timedelta
import string
from flask_mail import Message

from flask import request, Blueprint, session
from flask_jwt_extended import create_access_token, get_jwt, create_refresh_token, jwt_required, get_jwt_identity
from flask_login import login_user
from pydantic import ValidationError

from skraggle.base_helpers.orgGen import getOrg
from skraggle.decarotor import user_required, user_admin_required
from skraggle.base_helpers.responser import DataResponse
from skraggle.validators_logics.validators import AdminValidator
from .models import Admin, AccessTokenBlocklist
from werkzeug.security import generate_password_hash, check_password_hash
from skraggle.config import db
from .email_confirmation import confirm_token, eblaster, gen_token, generate_confirmation_token
from skraggle.run import mail
from skraggle.utils.generate_random_string import get_random_string

from .twofactor import gen_otp

adminprofile = Blueprint("adminprofile", __name__, template_folder="templates") 

@adminprofile.route("/login", methods=["POST"])
def admin_login():
    if request.method == "POST":
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        remember = True if request.json.get("remember") else False
        is_admin = Admin.query.filter_by(email=email).first()
        extra_protection = is_admin.extra_protection if is_admin else None
        authenticated = session.get("authenticated")
        if extra_protection and not authenticated:
            gen_otp(
                request.host_url,
                str(is_admin.first_name + " " + is_admin.last_name),
                email,
            )
            resp = DataResponse(
                False,
                f"2 Factor Authentication is enabled , please enter otp you received to proceed login",
            )
            return resp.status()
        if extra_protection and authenticated:
            login_user(is_admin, remember=remember)
            session["key"] = 123
            access_token = create_access_token(
                identity=is_admin.admin_id,
                additional_claims={
                    "is_admin": is_admin.is_admin,
                    "org": is_admin.organization_id,
                    "activated": is_admin.confirmed,
                    "email": is_admin.email,
                },
            )
            
            refresh_token = create_refresh_token(
                identity=is_admin.admin_id,
                additional_claims={
                    "is_admin": is_admin.is_admin,
                    "org": is_admin.organization_id,
                    "activated": is_admin.confirmed,
                    "email": is_admin.email,
                },
            )
            
            if not is_admin.confirmed:
                resp = DataResponse(
                    False, f"Please activate your account to log in",
                    401
                )
                return resp.status()
            login_data = {
                "statusCode": 200,
                "refresh": refresh_token,
                "access": access_token
            }
            resp = DataResponse(True, login_data)
            return resp.status()
        if is_admin and check_password_hash(is_admin.password, password):
            login_user(is_admin, remember=remember)
            access_token = create_access_token(
                identity=is_admin.admin_id,
                expires_delta=timedelta(days=1),
                additional_claims={
                    "is_admin": is_admin.is_admin,
                    "org": is_admin.organization_id,
                    "activated": is_admin.confirmed,
                    "email": is_admin.email,
                },
            )
            refresh_token = create_refresh_token(
                identity=is_admin.admin_id,
                additional_claims={
                    "is_admin": is_admin.is_admin,
                    "org": is_admin.organization_id,
                    "activated": is_admin.confirmed,
                    "email": is_admin.email,
                },
            )
            if not is_admin.confirmed:
                resp = DataResponse(
                    False, f"Please Activate your account to log in", 401
                )
                return resp.status()
            login_data = {
                "statusCode": 200,
                "refresh": refresh_token,
                "access": access_token
            }
            resp = DataResponse(True, login_data)
            return resp.status()
        # 2 Factor Authentication Code Block ---START

        # 2 Factor Authentication Code Block --- END
        resp = DataResponse(False, "Invalid Credentials", 401)
        return resp.status()


@adminprofile.route("/signup", methods=["POST"])
def admin_signup():
    email = request.json.get("email")
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    password = request.json.get("password")
    permission_level = request.json.get("permission_level", "administrator")
    admin_data = dict(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=generate_password_hash(password, method="sha256"),
        type_of=request.json.get("type_of", "user"),
        permission_level=permission_level,
    )
    
    is_admin = Admin.query.filter_by(email=email).first()
    if is_admin:
        resp = DataResponse(False, "User already exists")
        return resp.status()

    try:
        AdminValidator(**admin_data)
        try:
            new_admin = Admin(**admin_data)
            db.session.add(new_admin)
            db.session.flush()
            if permission_level == "administrator":
                new_admin.is_admin = True
                db.session.commit()
            success, confirmation_response = gen_token(email, new_admin)
            if not success:
                resp = DataResponse(False, confirmation_response)
                return resp.status()
            resp = DataResponse(True, confirmation_response)
            return resp.status()
        except Exception as e:
            resp = DataResponse(False, str(e))
            return resp.status()
    except ValidationError as e:
        return e.json()


'''
Reset password
'''
@adminprofile.route("/reset-password", methods=["POST"])
def reset_password():
    body = request.json
    token = body['token']
    email = body['email']
    try:
        admin = Admin.query.filter_by(email=email).first()
        
        if not admin or not admin.token_reset or admin.token_reset != token:
            return DataResponse(False, "This link is invalid!").status()

        password = get_random_string()
        admin.password = generate_password_hash(password, method="sha256")
        admin.token_reset = None
        db.session.commit()
        
        return DataResponse(True, f"Your password has been reset successfully. Your password is {password}. We recommend copying this and changing your password in your dashboard as soon as you log in. This page will not be shown again.").status()
    except Exception as e:
        return DataResponse(False, str(e)[:105], 500).status()


'''
Forgot password
'''
@adminprofile.route("/forgot-password", methods=["POST"])
def forgot_password():
    body = request.json
    email = body['email']

    try:
        admin = Admin.query.filter_by(email=email).first()

        if not admin:
            return DataResponse(False, 'No admin was found with this email address').status()

        token = get_random_string(6, string.digits)
        admin.token_reset = token
        db.session.commit()

        sent, error = send_forgot_password_mail(token, email)
        print(token)
        
        if not sent:
            return DataResponse(False, str(error)[:105]).status()

        return DataResponse(True, 'A link to reset your password has been sent to your email').status()
    except Exception as e:
        return DataResponse(False, str(e)[:105], 500).status()


"""Admin Logout Route"""
@adminprofile.route("/logout", methods=["DELETE"])
@user_required()
def admin_logout():
    try:
        jwt_payload = get_jwt()
        curr_admin = Admin.query.filter_by(
            organization_id = getOrg(jwt_payload), email=jwt_payload["email"]
        ).first()
        
        if curr_admin.extra_protection:
            session["authenticated"] = False
            session.permanent = True
        
        jti = jwt_payload["jti"]
        
        db.session.add(AccessTokenBlocklist(jti=jti, revoked_on=datetime.now()))
        db.session.commit()
        
        session.clear()
        resp = DataResponse(True, {"statusCode":200, "msg": "Logged out"})
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@adminprofile.route("/update", methods=["PATCH"])
@user_required()
def admin_update():
    updating_fields = ["email", "password", "first_name", "last_name"]
    email = get_jwt()["email"]
    try:
        curr_admin = Admin.query.filter_by(email=email).first()
        for keys in updating_fields:
            setattr(
                curr_admin,
                keys,
                None if not request.form[keys] else request.form[keys],
            )
            db.session.add(curr_admin)
            db.session.commit()
            resp = DataResponse(True, f"Credentials/Details are  Updated successfully")
            return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@adminprofile.route("/set-permission-level", methods=["PATCH"])
@user_admin_required()
def admin_permission_level():
    admin_id = request.form.get("admin_id")
    permission_level = request.form.get("permission_level")
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin:
        try:
            admin.permission_level = permission_level
            if permission_level == "administrator":
                admin.is_admin = True
            else:
                admin.is_admin = False
            db.session.commit()
            resp = DataResponse(True, f"Permission Level Updated to {permission_level}")
            return resp.status()
        except Exception as e:
            resp = DataResponse(False, str(e))
            return resp.status()
    else:
        resp = DataResponse(False, "Admin Does not exist")
        return resp.status()


def send_forgot_password_mail(token, email):
    try:
        msg = Message("[Important!] Your password reset request", recipients=[email])
        msg.body = token 
        msg.html = f"<h1>Your password reset token is <strong>{token}</strong></h1>"
        mail.send(msg)
        return True, None
    except Exception as e:
        return False, e
    


@adminprofile.route("/refresh", methods=["GET"])
@jwt_required(refresh=True)
def refresh_user_access_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    login_data = {
        "statusCode": 200,
        "access": access
    }
    resp = DataResponse(True, login_data)
    return resp.status()


@adminprofile.route("/temp/delete-admin", methods=["GET"])
def delete_admin():
    email = request.args.get('email')
    admin = Admin.query.filter_by(email = email).one_or_none()
    
    if not admin:
        return DataResponse(True, f'{email} does not exist').status()
    
    db.session.query(Admin).filter_by(email = email).delete()
    db.session.commit()

    return DataResponse(True, f'{email} has been deleted').status()