from sqlalchemy.dialects.postgresql import UUID

from src.app_config import ModelMixin, OrganizationMixin, db


class EventsInformation(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "EventsInformation"
    
    campaign_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Campaign.id'), nullable=True)

    name = db.Column(db.String(255))
    description = db.Column(db.String(255), nullable=False)
    event_image = db.Column(db.String(255), nullable=False)
    event_sold_out_message = db.Column(db.String(255), nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(255), nullable=False)
    zip_country = db.Column(db.Integer, nullable=False)
    enable_map = db.Column(db.Boolean, nullable=False)
    display_option = db.Column(db.String(100), nullable=False)
    total_participant = db.Column(db.Integer, nullable=False)
    enable_one_time_donation = db.Column(db.Boolean, nullable=False)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    event_has_reg_cutoff_date = db.Column(db.Boolean, nullable=False)
    admin_notification = db.Column(db.PickleType, nullable=False)
    reciept_type = db.Column(db.String(255), nullable=False)
    reciept_title = db.Column(db.String(255), nullable=False)
    reciept_category = db.Column(db.String(255), nullable=False)
    reciept_description = db.Column(db.String(255), nullable=False)
    sender_name = db.Column(db.String(255), nullable=False)
    reply_email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    archived = db.Column(db.Boolean, default=False)
    

    def __init__(self, 
        name,
        description,
        event_image,
        event_sold_out_message,
        venue,
        address,
        city,
        state,
        zip_country,
        enable_map,
        display_option,
        total_participant,
        enable_one_time_donation,
        start_at,
        end_at,
        event_has_reg_cutoff_date,
        admin_notification,
        reciept_type,
        reciept_title,
        reciept_category,
        reciept_description,
        sender_name,
        reply_email,
        subject,
        body,
        organization_id,
        archived=None,
        campaign_id=None
        ):
        self.name = name
        self.description = description
        self.event_image = event_image
        self.event_sold_out_message = event_sold_out_message
        self.venue = venue
        self.address = address
        self.city = city
        self.state = state
        self.zip_country = zip_country
        self.enable_map = enable_map
        self.display_option = display_option
        self.total_participant = total_participant
        self.enable_one_time_donation = enable_one_time_donation
        self.start_at = start_at
        self.end_at = end_at
        self.event_has_reg_cutoff_date = event_has_reg_cutoff_date
        self.admin_notification = admin_notification
        self.reciept_type = reciept_type
        self.reciept_title = reciept_title
        self.reciept_category = reciept_category
        self.reciept_description = reciept_description
        self.sender_name = sender_name
        self.reply_email = reply_email
        self.subject = subject
        self.body = body
        self.organization_id = organization_id
        self.archived = archived
        self.campaign_id = campaign_id
    
    
    @classmethod
    def register(cls, data: dict):
        if not data:
            raise Exception('Fields.register() requires an argument for `data`')

        # validations 
        required_fields = [
            'name','description','event_image',
            'event_sold_out_message','venue',
            'address','city','state','zip_country',
            'enable_map','display_option',
            'total_participant',
            'enable_one_time_donation',
            'start_at',
            'end_at',
            'event_has_reg_cutoff_date',
            'admin_notification',
            'reciept_type','reciept_title',
            'reciept_category','reciept_description',
            'sender_name','reply_email','subject','body',
            ]
          
        for field in required_fields:
            if field not in data.keys():
                return False, f"`{field}` is a required field"
               
        event = cls(**data)
        db.session.add(event)
        db.session.flush()
        db.session.commit()

        return True, event