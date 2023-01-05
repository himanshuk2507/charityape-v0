from skraggle.base_helpers.orgGen import getOrg
from skraggle.config import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
from flask_jwt_extended import get_jwt

import uuid

from skraggle.run import app


class Campaigns(db.Model):
    __schema__ = "Campaigns"
    __tablename__ = "Campaigns"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    forms = db.relationship(
        "Forms", backref="Campaigns", cascade="all,delete", lazy=True
    )
    associations = db.relationship(
        "Association", backref="Campaigns", cascade="all,delete", lazy=True
    )
    landing_page = db.relationship(
        "Elements", backref="Campaigns", cascade="all,delete", lazy=True
    )
    description = db.Column(db.String(200))
    fundraising_goal = db.Column(db.String(255), nullable=True)
    status = db.Column(ENUM("processing", "completed", name="campaign_status"),)
    assignee = db.Column(db.String(255), nullable=True)
    tags = db.Column(ARRAY(db.String(255)))
    followers = db.Column(ARRAY(UUID(as_uuid=True)))
    created_on = db.Column(db.DateTime, server_default=func.now())
    transactions = db.relationship(
        "Transactions", backref="Campaigns", lazy=True, cascade="all,delete",
    )

    def __init__(
        self,
        name,
        description,
        fundraising_goal,
        organization_id,
        assignee=None,
        followers = [],
        tags=[],
        created_on=None,
        status='processing',
    ):
        self.name = name
        self.description = description
        self.fundraising_goal = fundraising_goal
        self.assignee = assignee
        self.tags = tags
        self.followers = followers
        self.created_on = created_on
        self.status = status
        self.organization_id = organization_id

    def to_dict(self):
        campaigns = {
            "name": self.name,
            "description": self.description,
            "fundraising_goal": self.fundraising_goal,
            "assignee": self.assignee,
            "tags": self.tags,
            "followers": self.followers,
            "created_on": self.created_on,
            "status": self.status
        }
        return campaigns


class Association(db.Model):
    __schema__ = "Associations"
    __tablename__ = "Associations"

    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pledges = db.Column(UUID(as_uuid=True), db.ForeignKey("Pledges.id"))
    campaign = db.Column(UUID(as_uuid=True), db.ForeignKey("Campaigns.id"))
    impact_area = db.Column(db.String(255))
    source = db.Column(db.String(255))
    dedication = db.Column(db.String(255))
    note = db.Column(db.String(255))

    def __init__(self, pledges, impact_area, source, dedication, note=None):
        self.pledges = pledges
        self.impact_area = impact_area
        self.source = source
        self.dedication = dedication
        self.note = note

    def to_dict(self):
        association = {
            "pledges": self.pledges,
            "impact_area": self.impact_area,
            "source": self.source,
            "dedication": self.dedication,
            "campaign": self.campaign.to_dict(),
            "note": self.note
        }
        return association
