from skraggle.config import db
from skraggle.constants import BASE_URL
from skraggle.base_helpers.responser import DataResponse
from skraggle.profile.models import Invitations, Admin
import secrets


def invite_link_gen(invited_by, permission_level, invited_user_email,organization_id):
    user_exists = bool(Admin.query.filter_by(email=invited_user_email).first())
    if user_exists:
        return False
    invitation_key = secrets.token_urlsafe(12)
    invitation_data = dict(
        invited_by=invited_by,
        permission_level=permission_level,
        invited_user_email=invited_user_email,
        invitation_key=invitation_key,
        organization_id=organization_id
    )
    invite = Invitations(**invitation_data)
    db.session.add(invite)
    db.session.flush()
    curr_invite = Invitations.query.filter_by(
        invitation_id=invite.invitation_id
    ).first()
    invite_link = f"{BASE_URL}/invitation/{invitation_key}/sign-up"
    curr_invite.invitation_url = invite_link
    db.session.commit()
    return invite_link
