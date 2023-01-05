from datetime import datetime, timedelta
from flask import Blueprint, request, session
from flask_login import login_user
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity

from werkzeug.security import check_password_hash
from run import send_mail_in_background
from src.library.base_helpers.model_to_dict import model_to_dict
from src.library.decorators.authentication_decorators import admin_required, admin_with_email_exists
from src.library.html_templates.admin_auth_flow_templates import ForgotPasswordMailTemplate
from src.library.utility_classes.custom_validator import Validator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.library.utility_classes.text_generator import TextGenerator
from src.app_config import db
from .models import AccessTokenBlocklist, Admin


admin_endpoints = Blueprint('admin_endpoints', __name__)


'''
@route POST /admin
@desc Register a new Admin account 
@access Public
'''
@admin_endpoints.route("", methods=['POST'])
def signup_route():
    body = request.json
    result_bool, result_data = Admin.register(**body)

    return Response(result_bool, result_data).respond()

'''
@route POST /admin/request-verification
@desc Request a new email/OTP for verifying an Admin account
@access Public
'''
@admin_endpoints.route("/request-verification", methods=['POST'])
@admin_with_email_exists()
def request_verification_route(admin: Admin):
    # has this Admin been verified?
    if admin.confirmed:
        return Response(False, 'This email address has already been confirmed').respond()

    # generate new OTP
    admin.send_verification_mail()

    return Response(True, 'A new OTP has been sent to your mail').respond()

'''
@route POST /admin/verify-account
@desc Verify an Admin-account-confirmation OTP token
@access Public
'''
@admin_endpoints.route("/verify-account", methods=['POST'])
@admin_with_email_exists()
def verify_account_route(admin):
    token = request.json.get('token')

    # attempt to verify this Admin
    response = admin.confirm_account_with_otp(token)
    if not response:
        return Response(False, 'This token is either invalid or has expired').respond()
    
    return Response(True, admin.authorization_details).respond()

'''
@route POST /admin/login
@desc Authenticate & create a new access token
@access Public
'''
@admin_endpoints.route("/login", methods=['POST'])
def login_route():
    body = request.json
    email = body.get('email')
    password = body.get('password')

    # validations 
    if not email or not Validator.is_email(email):
        return Response(False, 'A valid email address is required').respond()
    if not password:
        return Response(False, '`password` is a required field').respond()

    # does this Admin exist?
    admin: Admin = Admin.fetch_one_by_email(email)
    if not admin:
        # use the Obfuscation Principle to mitigate brute-force attacks by returning a generic messsage that
        # does not tell the client that the email isn't registered
        return Response(False, 'This email address or password is incorrect', 401).respond()

    # has this Admin's email been verified?
    if not admin.confirmed:
        return Response(False, 'Verify your email address to sign in').respond()

    # does this password match hash?
    if not check_password_hash(admin.password, password):
        return Response(False, 'This email address or password is incorrect', 401).respond()

    # authenticate user
    login_user(admin, remember=True, force=True)

    return Response(True, admin.authorization_details).respond()

'''
@route GET /admin
@desc Fetch profile information for authenticated Admin
@access Admin
'''
@admin_endpoints.route("", methods=['GET'])
@admin_required()
def whoami_route():
    id = get_jwt().get('id')
    organization_id = get_jwt().get('organization_id')

    data = model_to_dict(Admin.fetch_one_by_id(
        id=id, org_id=organization_id
    ))

    return Response(True, data).respond()


'''
@route PATCH /admin
@desc Update Admin profile
@access Admin
'''
@admin_endpoints.route("", methods=['PATCH'])
@admin_required()
def update_admin_profile_route():
    body = request.json 

    unallowed_fields = ['id', 'organization_id', 'password']
    try:
        admin: Admin = Admin.fetch_one_by_id(get_jwt().get('id'), org_id=get_jwt().get('org_'))
    
        for field in body.keys():
            if field not in unallowed_fields:
                setattr(admin, field, body.get(field))
        db.session.commit()
        return Response(True, model_to_dict(admin)).respond()
    except Exception as e:
        print(e)
        return Response(False, 'An error occurred').respond()

'''
@route GET /admin/access-token
@desc Refresh access token
@access Admin
'''
@admin_endpoints.route("/access-token", methods=['GET'])
@jwt_required(refresh=True)
def refresh_access_token_route():
    id = get_jwt_identity()
    admin: Admin = Admin.fetch_one_by_id(id)
    print(admin)
    access_token = admin.create_access_token()

    return Response(True, dict(access_token=access_token)).respond()

'''
@route DELETE /admin/access-token
@desc Revoke access token/log out from client
@access Admin
'''
@admin_endpoints.route("/access-token", methods=['DELETE'])
@admin_required()
def revoke_access_token_route():
    try:
        claims = get_jwt()
        id = claims.get('id')

        jti = claims.get('jti')
        db.session.add(
            AccessTokenBlocklist(
                jti=jti
            )
        )
        db.session.commit()
        session.clear()

        return Response(True, 'You are now logged out').respond()
    except Exception as e:
        print(e)
        return Response(False, 'An error occurred').respond()

'''
@route POST /admin/password
@desc Reset password
@access Public
'''
@admin_endpoints.route("/password", methods=['POST'])
@admin_with_email_exists()
def reset_password_route(admin: Admin):
    try:
        # generate OTP and send mail
        otp = TextGenerator(length=6).otp()
        print(otp)

        admin.last_generated_token = otp
        admin.token_generated_at = datetime.now()
        db.session.commit()

        mail_body = f'Use this OTP ({otp}) to reset your password. Valid for 10 minutes.'
        send_mail_in_background.delay(mail_options=dict(
            subject='[Important] Password reset for your Skraggle account',
            recipients=[admin.email],
            text=mail_body,
            html=ForgotPasswordMailTemplate().render(name=admin.first_name, otp=otp)
        ))

        return Response(True, 'An OTP has been sent to your mail').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e)[:105], 500).respond()

'''
@route POST /admin/password/confirm
@desc Confirm an OTP token to finalise resetting an Admin account's password
@access Public
'''
@admin_endpoints.route("/password/confirm", methods=['POST'])
@admin_with_email_exists()
def confirm_password_reset_route(admin: Admin):
    token = request.json.get('token')
    if not token:
        return Response(False, 'A `token` field is required').respond()

    now = datetime.now()
    validity = timedelta(minutes=10)

    if admin.last_generated_token == token and now <= admin.token_generated_at + validity:
        # OTP is valid
        admin.last_generated_token = None 
        admin.token_generated_at = None
        result_bool, result_data = admin.change_password()
        
        if result_bool:
            return Response(True, result_data).respond()
        return Response(False, 'An error occurred', 500).respond()

    return Response(False, 'This token is invalid or has expired').respond()

'''
@route PATCH /admin/password
@desc Change password (this endpoint can only be called by an authenticated user! It is not the same as the Reset Password endpoint)
@access Admin
'''
@admin_endpoints.route("/password", methods=['PATCH'])
@admin_required()
def change_password_route():
    body = request.json 
    old_password = body.get('old')
    new_password = body.get('new')

    if not old_password or not new_password:
        return Response(False, '`old` and `new` are required fields').respond()

    # does old password match?
    admin: Admin = Admin.fetch_one_by_id(get_jwt().get('id'))
    if not check_password_hash(admin.password, old_password):
        return Response(False, '"old password" is incorrect', 403).respond()

    # change password
    admin.change_password(new_password)
    return Response(True, 'Your password has been updated successfully').respond()