from datetime import datetime, timedelta

import pytest
from skraggle.config import db
from skraggle.profile.models import Admin
from flask_jwt_extended import create_access_token
from skraggle.tests.integration.test_admin_auth import credentials
from skraggle.contact.models import SegmentUsers
from uuid import uuid1


"""
Creates an Admin account that can be used throughout the test session
"""
@pytest.fixture(scope="session")
def user():
    user = Admin.query.filter_by(email=credentials['email']).first()
    
    if user:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        user.is_admin = True

        db.session.commit()
        return user, access_token(user)
    
    user = Admin(**credentials)
    user.confirmed = True
    user.confirmed_on = datetime.now()
    user.is_admin = True
    
    db.session.add(user)
    db.session.flush()
    db.session.commit()

    return user, access_token(user)


"""
Creates a SegmentUsers object that can be used throughout the test session
"""
def segmentuser(retrieve_new=False):
    segment = SegmentUsers.query.first()

    if retrieve_new == False and segment:
        db.session.commit()
        return segment

    segment = SegmentUsers(
        name="test",
        description="test",
        contacts=[uuid1(), uuid1()],
        created_on=datetime.now()
    )

    db.session.add(segment)
    db.session.flush()
    db.session.commit()  

    return segment  


def access_token(user):
    access_token = create_access_token(
        identity=user.admin_id,
        expires_delta=timedelta(days=1),
        additional_claims={
            "is_admin": user.is_admin,
            "org": user.organization_id,
            "activated": user.confirmed,
            "email": user.email,
        },
    )

    return access_token