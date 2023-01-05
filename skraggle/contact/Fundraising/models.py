from skraggle.config import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
import uuid
from skraggle.run import app


class Transactions(db.Model):
    __tablename__ = "Transactions"
    __schema__ = "transactions"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    transaction_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    donor_id = db.Column(UUID(as_uuid=True), db.ForeignKey("Donors.donor_id"))
    campaign_id = db.Column(UUID(as_uuid=True), db.ForeignKey("Campaigns.id"))
    dateReceived = db.Column(db.DateTime)
    transactionType = db.Column(db.String(255))
    totalAmount = db.Column(db.Float)
    receipts = db.relationship("TransactionReceipts", backref="Transactions", lazy=True)
    status = db.Column(
        ENUM("accepted", "declined", "pending", name="transaction_status")
    )
    transaction_info = db.Column(JSONB, default={})
    attachments = db.Column(db.String(255))
    billing_address = db.Column(db.String(255))
    transaction_by = db.Column(UUID(as_uuid=True), nullable=True)
    transaction_from = db.Column(
        ENUM(
            "from_donor",
            "from_contact",
            "from_pledge",
            "from_event",
            name="transaction_from_field",
        )
    )
    transaction_for = db.Column(
        ENUM(
            "donation",
            "revenue",
            "other",
            name="transaction_for",
        )
    )

    def __init__(
        self,
        dateReceived,
        transactionType,
        totalAmount,
        billing_address,
        transaction_by,
        transaction_from,
        transaction_for
    ):
        self.dateReceived = dateReceived
        self.transactionType = transactionType
        self.totalAmount = totalAmount
        self.billing_address = billing_address
        self.transaction_by = transaction_by
        self.transaction_from = transaction_from
        self.transaction_for = transaction_for



class TransactionReceipts(db.Model):
    __tablename__ = "TransactionReceipts"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    receiptID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("Transactions.transaction_id")
    )
    receipt_name = db.Column(db.String(255))
    full_address = db.Column(db.String(255))
    delivery_option = db.Column(db.String(255))
    email = db.Column(db.String(255))

    def __init__(self, receipt_name, full_address, delivery_option, email):
        self.receipt_name = receipt_name
        self.full_address = full_address
        self.delivery_option = delivery_option
        self.email = email
