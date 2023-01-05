import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt
from werkzeug.security import generate_password_hash
from skraggle.config import db
from skraggle.decarotor import admin_required, user_admin_required
from skraggle.base_helpers.eblast_email_fetch import email_extracter
from skraggle.base_helpers.invite_link_generator import invite_link_gen
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.profile.email_confirmation import gen_token
from skraggle.profile.models import Invitations, Admin
from skraggle.validators_logics.validators import AdminValidator

invitationview = Blueprint("invitationview", __name__, template_folder="templates")


@invitationview.route("/<invitation_key>/sign-up", methods=["POST"])
def invite_sign_up(invitation_key):
    invitation = Invitations.query.filter_by(invitation_key=invitation_key).first()
    keyExpired = True if (datetime.now() - invitation.invited_on).days < 2 else False
    if invitation and not invitation.expired and keyExpired:
        email = request.form["email"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = generate_password_hash(request.form["password"], method="sha256")
        if invitation.invited_user_email == email:
            new_admin = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "password": password,
                "type_of": "invitation",
                "permission_level": invitation.permission_level,
            }
            try:
                AdminValidator(**new_admin)
                add_user = Admin(**new_admin)
                db.session.add(add_user)
                db.session.flush()
                add_user.organization_id = (invitation.organization_id,)
                if invitation.permission_level == "administrator":
                    add_user.is_admin = True
                    invitation.expired = True
                db.session.commit()
                gen_token(email)
                resp = DataResponse(
                    True,
                    "An Email Confirmation link has been sent to your email address , Please Confirm to activate your "
                    "Account",
                )
                return resp.status()
            except Exception as e:
                resp = DataResponse(False, str(e))
                return resp.status()
        else:
            resp = DataResponse(
                False,
                "Email ID Does not match with invite Link,Try registering with the email that received the invite link",
            )
            return resp.status()
    else:
        resp = DataResponse(False, "Invitation Link Expired or Not Valid")
        return resp.status()


@invitationview.route("/generate", methods=["POST"])
@user_admin_required()
def invite_generate():
    inviting_user_email = request.form["email"]
    invited_user_email = get_jwt()["email"]
    admin = (
        Admin.query.filter_by(email=invited_user_email,organization_id=getOrg(get_jwt())).first()
    )
    invited_by = admin.admin_id
    permission_level = request.form["permission_level"]
    organization_id = getOrg(get_jwt())
    invite_link = invite_link_gen(
        invited_by, permission_level, inviting_user_email, organization_id
    )
    if not invite_link:
        resp = DataResponse(
            False, "Cannot generate invite link,User email already exists in Team"
        )
        return resp.status()
    resp = DataResponse(True, invite_link)
    return resp.status()
