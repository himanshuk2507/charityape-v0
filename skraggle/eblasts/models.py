from skraggle.config import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY, JSONB
import uuid
from sqlalchemy.ext.mutable import Mutable, MutableDict

from skraggle.run import app


class MutableList(Mutable, list):
    def add(self, value):
        list.append(self, value)
        self.changed()

    def remove(self, value):
        list.remove(self, value)
        self.changed()


    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


class Eblasts(db.Model):
    __tablename__ = "Eblasts"
    __schema__ = "eblasts"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    eblast_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    eblast_name = db.Column(db.String(255))
    campaign_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    assignee = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    category_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    status = db.Column(
        ENUM("draft", "sent", "archive", name="eblast_status"), default="draft"
    )
    created_on = db.Column(db.DateTime(), default=func.now())
    sent_date = db.Column(db.DateTime(), nullable=True)
    eblast_content = db.relationship(
        "EblastsContent", backref="Eblasts", lazy=True, cascade="all,delete"
    )
    stats = db.Column(
        MutableDict.as_mutable(JSONB),
        default={
            "delivered": None,
            "opened": None,
            "clicked": None,
            "unopened": None,
            "amount_raised": None,
            "unsubscribed": None,
            "rejected": None,
        },
    )
    amount_raised = db.Column(db.Integer)

    def __init__(self, eblast_name, campaign_id, assignee, category_id):
        self.eblast_name = eblast_name
        self.campaign_id = campaign_id
        self.assignee = assignee
        self.category_id = category_id

    def to_dict(self):
        eblast_info = {
            "eblast_id": self.eblast_id,
            "eblast_name": self.eblast_name,
            "campaign_id": self.campaign_id,
            "assignee": self.assignee,
            "category_id": self.category_id,
            "status": self.status,
            "eblast_created_on": self.created_on,
            "sent_date": self.sent_date
            if self.status == "sent"
            else "eblast still in draft state",
        }
        return eblast_info

    def eblast_stats(self):
        eblast_stats = {
            "delivered": self.stats["delivered"],
            "opened": self.stats["opened"],
            "clicked": self.stats["clicked"],
            "unopened": self.stats["unopened"],
            "amount_raised": self.stats["amount_raised"],
            "unsubscribed": self.stats["unsubscribed"],
            "rejected": self.stats["rejected"],
        }
        return eblast_stats


class EblastsContent(db.Model):
    __tablename__ = "EblastsContent"
    __schema__ = "eblasts"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    eblasts_content_id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    eblast = db.Column(UUID(as_uuid=True), db.ForeignKey("Eblasts.eblast_id"))
    eblast_users = db.Column(
        ENUM(
            "segment", "tags", "contacts", name="eblasts_send_type", default="contacts"
        )
    )
    segment_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    tag_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    send_to = db.Column(
        MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=True
    )
    mail_from = db.Column(db.String(255))
    sender_name = db.Column(db.String(255))
    reply_to = db.Column(MutableList.as_mutable(ARRAY(UUID(as_uuid=True))))
    send_to_unknown = db.Column(db.Boolean, default=False)
    subject = db.Column(db.String(255))
    attachments = db.Column(
        MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=True
    )
    content = db.Column(db.Text, nullable=True)
    exclude = db.Column(db.Boolean, default=False)
    _exclude_emails =  db.Column(
        MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=True
    )

    def __init__(
        self,
        eblast_users,
        segment_id,
        tag_id,
        send_to,
        mail_from,
        subject,
        attachments,
        sender_name,
        reply_to,
        send_to_unknown,
        content,
    ):
        self.eblast_users = eblast_users
        self.segment_id = segment_id
        self.tag_id = tag_id
        self.send_to = send_to
        self.mail_from = mail_from
        self.subject = subject
        self.attachments = attachments
        self.sender_name = sender_name
        self.reply_to = reply_to
        self.send_to_unknown = send_to_unknown
        self.content = content

    def to_dict(self):
        eblast_content = {
            "eblast": self.eblast,
            "eblast_users": self.eblast_users,
            "segment_id": self.segment_id,
            "tag_id": self.tag_id,
            "send_to": self.send_to,
            "mail_from": self.mail_from,
            "subject": self.subject,
            "attachments": self.attachments,
            "sender_name": self.sender_name,
            "reply_to": self.reply_to,
            "send_to_unknown": self.send_to_unknown,
            "content": self.content,
        }
        return eblast_content
