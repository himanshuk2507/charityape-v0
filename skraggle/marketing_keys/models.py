from skraggle.config import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from sqlalchemy.ext.mutable import MutableDict

from skraggle.run import app


class MarketingKeys(db.Model):
    __schema__ = "Marketing"
    __tablename__ = "MarketingKeys"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey("Admin.admin_id"))
    google_analytics = db.Column(MutableDict.as_mutable(JSONB))
    facebook_pixel = db.Column(MutableDict.as_mutable(JSONB))
    facebook_conversion = db.Column(MutableDict.as_mutable(JSONB))

    def __str__(self):
        return str(self.id)

    def to_dict(self):
        d = {
            "id": self.id,
            "admin_id": self.admin_id,
            "google_analytics": self.google_analytics,
            "facebook_pixel": self.facebook_pixel,
            "facebook_conversion": self.facebook_conversion
        }
        return d
