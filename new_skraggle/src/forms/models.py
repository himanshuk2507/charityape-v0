from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db


class Form(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'Form'

    name = db.Column(db.String(255))
    type = db.Column(db.String(200))
    campaign_id = db.Column(UUID(as_uuid=True), db.ForeignKey("Campaign.id"))
    amount_raised = db.Column(db.Integer(), nullable=True)
    donations_count = db.Column(db.Integer(), nullable=True)
    status = db.Column(db.String(25), nullable=False, default="active")
    archived = db.Column(db.Boolean, nullable=False, default=False)

    auto_tag = db.Column(db.Boolean, default=False, nullable=True)
    form_flow = db.Column(db.Boolean, default=True, nullable=True)
    request_personal_details_before_checkout = db.Column(db.Boolean, nullable=False, default=False)
    use_donor_accounts = db.Column(db.Boolean, default=True, nullable=False)
    use_offline_payment = db.Column(db.Boolean, default=True, nullable=False)
    events_link_on_first_page = db.Column(db.Boolean, default=True, nullable=False)

    # Donation Setup
    default_currency = db.Column(db.String(20), nullable=True)
    currency_change_allowed = db.Column(db.Boolean, default=False, nullable=False)
    change_currency_for = db.Column(db.String(70), nullable=True)
    recurring_giving = db.Column(db.String(70), nullable=True)
    recurring_gift_suggestion = db.Column(db.String(45), nullable=True)  # before, after checkout or both
    recurring_default = db.Column(db.String(40), nullable=True)  # monthly, quarterly, yearly

    # Donation Amounts
    donation_amount = db.Column(db.Integer, nullable=True)
    amount_presets = db.Column(ARRAY(db.Integer), nullable=True)
    designation_cause_from = db.Column(db.Boolean, nullable=True, default=True)
    designation = db.Column(db.String(255), nullable=True)
    enable_comments = db.Column(db.Boolean, nullable=True, default=True)
    enable_tribute = db.Column(db.Boolean, nullable=True, default=True)

    # Processing Fee
    transaction_cost = db.Column(db.String(120), nullable=True)  # Coverage of transaction cost

    # Supporter Tab
    ask_mailing_address = db.Column(db.Boolean, nullable=True, default=True)
    ask_phone_number = db.Column(db.Boolean, nullable=True, default=True)
    anonymous_donation_allowed = db.Column(db.Boolean, nullable=True, default=True)
    company_donations_allowed = db.Column(db.Boolean, nullable=True, default=True)

    # Thank you page
    thank_you_screen = db.Column(db.Boolean(), nullable=True)
    redirection = db.Column(db.String(15), nullable=True)

    # URL
    checkout_url = db.Column(db.String(255), nullable=True)

    def __init__(
            self, name=None, type=None, status="active", 
            campaign_id=None, organization_id=None
    ):
        self.name = name
        self.type = type
        self.status = status
        self.campaign_id = campaign_id
        
        self.organization_id = organization_id
        

    @classmethod
    def register(cls, data: dict = None):
        if not data:
            raise Exception('Form.register() requires an argument for `data`')

        # validations
        required_fields = ['name', 'type', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"

        try:
            # does campaign with this name already exist?
            form = cls.query.filter_by(
                name=data.get('name'),
                organization_id=data.get('organization_id')
            ).one_or_none()
            if form:
                return False, "A form is already registered with this name. Try again with a different name."

            form = Form(**data)
            db.session.add(form)
            db.session.flush()
            db.session.commit()

            return True, form
        except Exception as e:
            print(str(e))
            return False, str(e)

    def update(self, data: dict = None):
        if not data:
            raise Exception('Form.update() requires an argument for `data`')

        try:
            unallowed_fields = ['id', 'organization_id']
            for field in data.keys():
                if field not in unallowed_fields:
                    setattr(self, field, data.get(field))

            db.session.add(self)
            db.session.commit()

            return True, self
        except Exception as e:
            print(e)
            return False, str(e)
