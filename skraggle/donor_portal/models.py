import uuid
from sqlalchemy.dialects.postgresql import UUID, ENUM
from skraggle.config import db
from skraggle.run import app


class DonorPortal(db.Model):
    __tablename__ = "DonorPortal"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True,
    )
    portal_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portal_url = db.Column(db.String(255), nullable=True)
    browse_icon = db.Column(db.String(255), nullable=True)
    header_image = db.Column(db.String(255), nullable=True)
    hero_image = db.Column(db.String(255), nullable=True)
    portal_title = db.Column(db.String(255), nullable=True)
    recurring_donation_cancellation = db.Column(db.Boolean, default=True)
    reduce_donation_amount = db.Column(db.Boolean, default=True)
    skip_recurring_donation = db.Column(db.Boolean, default=False)

    def __init__(
        self,
        portal_url,
        browse_icon,
        header_image,
        hero_image,
        portal_title,
        recurring_donation_cancellation,
        reduce_donation_amount,
        skip_recurring_donation,
    ):
        self.portal_url = portal_url
        self.browse_icon = browse_icon
        self.header_image = header_image
        self.hero_image = hero_image
        self.portal_url = portal_url
        self.portal_title = portal_title
        self.recurring_donation_cancellation = recurring_donation_cancellation
        self.reduce_donation_amount = reduce_donation_amount
        self.skip_recurring_donation = skip_recurring_donation



