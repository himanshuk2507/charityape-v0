from skraggle.config import db
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid

from skraggle.run import app


class Elements(db.Model):
    __schema__ = "Campaigns"
    __tablename__ = "Elements"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    campaign_id = db.Column(UUID(as_uuid=True), db.ForeignKey("Campaigns.id"))
    internal = db.Column(db.Integer(), default=0)
    external = db.Column(db.Integer(), default=0)
    source_code = db.Column(db.Text)
    type = db.Column(
        ENUM("internal", "external", name="elements", create_type=False), nullable=False
    )
    disabled=db.Column(db.Boolean, default=False, nullable=False)
    archive=db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        elements = {
            "id": self.id,
            "name": self.name,
            "campaign_id": self.campaign_id,
            "type": self.type,
            "internal": self.internal,
            "external": self.external

        }
        return elements
