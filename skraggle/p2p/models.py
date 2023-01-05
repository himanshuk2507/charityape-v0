from email.policy import default
from flask import session
from skraggle.config import db
import uuid
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
from sqlalchemy import func
from sqlalchemy.ext.mutable import Mutable

from skraggle.run import app


class MutableList(Mutable, list):
    def award(self, value):
        list.append(self, value)
        self.changed()

    def revoke(self, value):
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


class Participants(db.Model):
    __tablename__ = "Participants"
    __schema__ = "constituents"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    participant_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    donation_amount = db.Column(db.Integer)
    category = db.Column(db.String(255))
    badges_list = db.Column(MutableList.as_mutable(ARRAY(UUID(as_uuid=True))))
    classification = db.Column(db.String(255))
    is_team_captain = db.Column(db.Boolean, default=False)
    in_team = db.Column(db.Boolean, default=False)
    team = db.Column(UUID(as_uuid=True), db.ForeignKey("P2pTeams.participants"))

    def __init__(
            self, first_name, last_name, address, full_name, phone_number, donation_amount
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = full_name
        self.donation_amount = donation_amount
        self.address = address
        self.phone_number = phone_number

    def to_dict(self):
        participant_info = {
            "fullname": self.full_name,
            "lastname": self.last_name,
            "firstname": self.first_name,
            "donation_amount": self.donation_amount,
            "address": self.address,
            "phone_number": self.phone_number,
            "Badges": self.badges,
            "is_team_captain": self.is_team_captain,
            "in_team": self.in_team,
            "team": self.team,
            "badges": self.badges_list,
        }

        return participant_info


class Badges(db.Model):
    __tablename__ = "Badges"
    __schema__ = "Badges"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    badge_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    badge_name = db.Column(db.String(255))
    badge_color = db.Column(db.String(255))
    badge_icon = db.Column(db.String(255))
    badge_type = db.Column(
        ENUM("custom", "system", name="badge_type", create_type=False, )
    )
    uploaded_batch = db.Column(db.String(255))
    badge_restriction = db.Column(
        ENUM(
            "any_participant",
            "team_members",
            "team_captain",
            "team",
            name="badge_restriction",
            create_type=False,
        )
    )
    badge_status = db.Column(
        ENUM("disable", "enable", name="badge_status", create_type=False)
    )
    manually_award = db.Column(db.Boolean, default=False)
    achievement_reached_type = db.Column(
        ENUM(
            "individual_donations",
            "percentage_of_donations",
            "total_donations",
            name="achievement_status",
            create_type=False,
        ),
        nullable=False,
    )
    achievement_reached = db.Column(db.Integer)
    badge_award = db.Column(
        ENUM(
            "manually",
            "achievement",
            "engagement",
            name="badge_award",
            create_type=False,
        ),
        nullable=False,
    )

    def __init__(
            self,
            badge_name,
            badge_color,
            badge_icon,
            badge_restriction,
            badge_status,
            badge_award,
            achievement_reached_type,
            achievement_reached,
            manually_award,
            uploaded_batch,
            badge_type,
    ):
        self.badge_name = badge_name
        self.badge_color = badge_color
        self.badge_icon = badge_icon
        self.badge_restriction = badge_restriction
        self.badge_status = badge_status
        self.badge_award = badge_award
        self.uploaded_batch = uploaded_batch
        self.achievement_reached_type = achievement_reached_type
        self.achievement_reached = achievement_reached
        self.manually_award = manually_award
        self.badge_type = badge_type


class P2pEventInformation(db.Model):
    __tablename__ = "P2PEventInformation"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    internal_event_name = db.Column(db.String(250))
    event_name = db.Column(db.String(250))
    event_status = db.Column(
        ENUM("Active", "Disabled", "Closed",
             name="eventInformation", create_type=False), nullable=False
    )
    fundraising_goal = db.Column(db.Integer)
    event_start_date = db.Column(db.DateTime, nullable=False, default=func.now)
    event_end_date = db.Column(db.DateTime, nullable=False, default=func.now)
    event_registration_cutoff_date = db.Column(db.DateTime, nullable=False, default=func.now)

    def to_dict(self):
        eventinfo = {
            "internal_event_name": self.internal_event_name,
            "event_name": self.event_name,
            "event_status": self.event_status,
            "fundraising_goal": self.fundraising_goal,
            "event_start_date": self.event_start_date,
            "event_end_date": self.event_end_date,
            "event_registration_cutoff_date": self.event_registration_cutoff_date
        }
        return eventinfo


class P2pEventContactInformation(db.Model):
    __tablename__ = "P2pEventContactInformation"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_first_name = db.Column(db.String(255))
    contact_last_name = db.Column(db.String(255))
    contact_email = db.Column(db.String(255))
    contact_address = db.Column(db.String(255))
    contact_phone_number = db.Column(db.Integer)
    from_email_address = db.Column(db.String(250))

    from_name = db.Column(db.String(50))

    def __init__(self, contact_first_name, contact_last_name, contact_email, contact_address, contact_phone_number,
                 from_email_address, from_name):
        self.contact_first_name = contact_first_name
        self.contact_last_name = contact_last_name
        self.contact_email = contact_email
        self.contact_address = contact_address
        self.contact_phone_number = contact_phone_number
        self.from_email_address = from_email_address
        self.from_name = from_name

    def to_dict(self):
        eventcontact = {
            "contact_first_name": self.contact_first_name,
            "contact_last_name": self.contact_last_name,
            "contact_email": self.contact_email,
            "contact_address": self.contact_address,
            "contact_phone_number": self.contact_phone_number,
            "from_email_address": self.from_email_address,
            "from_name": self.from_name
        }
        return eventcontact


class P2pClassification(db.Model):
    __tablename__ = "p2pClassification"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    time_zone = db.Column(
        ENUM(
            "Eastern Time",
            "Central Time",
            "Mountain Time",
            "Pacific Time",
            "Alaska Time",
            "Hawaii Time",
            name="timezone",
            create_type=False,
        ),
        nullable=False,
    )

    def __init__(self, name, description, time_zone):
        self.name = name
        self.description = description
        self.time_zone = time_zone

    def to_dict(self):
        classification = {
            "name": self.name,
            "description": self.description,
            "time_zone": self.time_zone,
        }
        return classification


class P2pCategories(db.Model):
    __tablename__ = "P2pCategories"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    promocodes = db.relationship(
        "P2pPromoCode", backref="P2pCategories", cascade="all,delete", lazy=True
    )

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def to_dict(self):
        categories = {
            "name": self.name,
            "description": self.description
        }
        return categories


class P2pPromoCode(db.Model):
    __tablename__ = "P2pPromoCode"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    promo_code = db.Column(db.String(255))
    description = db.Column(db.String(255))
    discount = db.Column(db.Integer)
    max_user = db.Column(db.Integer)
    start_date = db.Column(db.DateTime, nullable=False, default=func.now)
    end_date = db.Column(db.DateTime, nullable=False, default=func.now)
    category = db.Column(UUID(as_uuid=True), db.ForeignKey("P2pCategories.id"))

    def __init__(self, promo_code, description, discount, max_user, start_date, end_date):
        self.promo_code = promo_code
        self.description = description
        self.discount = discount
        self.max_user = max_user
        self.start_date = start_date
        self.end_date = end_date

    def to_dict(self):
        promocode = {
            "promo_code": self.promo_code,
            "description": self.description,
            "max_user": self.max_user,
            "start_date": self.start_date,
            "end_date": self.end_date
        }
        return promocode


class P2pDedication(db.Model):
    __tablename__ = "P2pDedication"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dedication_text = db.Column(db.String(255))

    def __init__(self, dedication_text):
        self.dedication_text = dedication_text

    def to_dict(self):
        dedication = {
            "dedication_text": self.dedication_text,
        }
        return dedication


class P2pDonationAmount(db.Model):
    __tablename__ = "P2pDonationAmount"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = db.Column(db.Integer)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))

    def __init__(self, amount, name, description):
        self.amount = amount
        self.name = name
        self.description = description

    def to_dict(self):
        donation = {
            "amount": self.amount,
            "name": self.name,
            "description": self.description
        }
        return donation


class P2pRestrictions(db.Model):
    __tablename__ = "P2pRestrictions"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def to_dict(self):
        restriction = {
            "name": self.name,
            "description": self.description
        }
        return restriction


class StoreProduct(db.Model):
    __tablename__ = "StoreProduct"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String)
    description = db.Column(db.String)
    category = db.Column(UUID(as_uuid=True), db.ForeignKey("StoreCategories.id"))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def to_dict(self):
        product = {
            "name": self.name,
            "description": self.description
        }
        return product


class StoreCategories(db.Model):
    __tablename__ = "StoreCategories"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    store_product = db.relationship(
        "StoreProduct", backref="StoreCategories", cascade="all,delete", lazy=True
    )

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        categories = {
            "name": self.name,
        }
        return categories


class P2pTeams(db.Model):
    __tablename__ = "P2pTeams"
    __schema__ = "teams"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    team_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    participants = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    team_name = db.Column(db.String(255))
    team_members = db.relationship(
        "Participants", backref="P2pTeams", cascade="all,delete", lazy=True
    )
    badges = db.Column(MutableList.as_mutable(ARRAY(UUID(as_uuid=True))))
    captain = db.Column(UUID(as_uuid=True), nullable=True)
    verified_amount = db.Column(db.Integer)
    unverified_amount = db.Column(db.Integer)
    amount_raised = db.Column(db.Integer)
    team_avatar = db.Column(db.String(255), nullable=True)
    created_on = db.Column(db.DateTime, nullable=False, default=func.now())

    def __init__(
            self,
            team_name: str,
            captain,
            verified_amount: int = 0,
            unverified_amount: int = 0,
            amount_raised: int = 0,
            team_avatar: str = None,
    ):
        self.team_name = team_name
        self.captain = captain
        self.team_avatar = team_avatar
        self.verified_amount = verified_amount
        self.unverified_amount = unverified_amount
        self.amount_raised = amount_raised

    def to_dict(self):
        team_dict = {
            "team_name": self.team_name,
            "amount_raised": self.amount_raised,
            "verified_amount": self.verified_amount,
            "unverified_amount": self.unverified_amount,
            "captain": self.captain,
            "team_avatar": self.team_avatar,
            "team_badges": self.badges,
        }
        return team_dict


class SponsorCategories(db.Model):
    __tablename__ = "SponsorCategories"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name = db.Column(db.String(255))

    def __init__(self, category_name):
        self.category_name = category_name


class Resource(db.Model):
    __tablename__ = "Resource"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file = db.Column(db.String(255))
    title = db.Column(db.String(255))
    category = db.Column(
        ENUM("image", "document", "other", name="resource", create_type=False, ),
        nullable=False,
    )

    def to_dict(self):
        resource = {
            "file": self.file,
            "title": self.title,
            "category": self.category
        }
        return resource


class InappropriateContent(db.Model):
    __tablename__ = "InappropriateContent"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    url_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = db.Column(db.String(255))
    url_status = db.Column(
        ENUM("blocked", "cleared", "flagged", name="url_status", create_type=False, ),
        nullable=False,
    )

    def __init__(self, url_status, url):
        self.url = url
        self.url_status = url_status

    def to_dict(self):
        inappropriate_urls = {"url": self.url, "url_status": self.url_status, "url_id": self.url_id}
        return inappropriate_urls


class WelcomeGuests(db.Model):
    __tablename__ = "WelcomeGuests"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    walkthrough = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    welcome_quest = db.Column(db.Boolean, default=True)
    upload_your_avatar = db.Column(db.Boolean, default=True)
    update_your_personal_page = db.Column(db.Boolean, default=True)
    send_a_fundraising_email = db.Column(db.Boolean, default=True)
    raise_your_first_donation = db.Column(db.Boolean, default=True)
    recruit_a_team_member = db.Column(db.Boolean, default=True)
    share_on = db.Column(db.Boolean, default=True)
    steps = db.Column(db.Integer)

    def __init__(
            self,
            welcome_quest,
            upload_your_avatar,
            update_your_personal_page,
            send_a_fundraising_email,
            raise_your_first_donation,
            recruit_a_team_member,
            share_on,
    ):
        self.welcome_quest = welcome_quest
        self.upload_your_avatar = upload_your_avatar
        self.update_your_personal_page = update_your_personal_page
        self.send_a_fundraising_email = send_a_fundraising_email
        self.raise_your_first_donation = raise_your_first_donation
        self.recruit_a_team_member = recruit_a_team_member
        self.share_on = share_on

    def to_dict(self):
        walthrough = {
            "walkthrough_id": self.walkthrough,
            "welcome_quest": self.welcome_quest,
            "upload_your_avatar": self.upload_your_avatar,
            "update_your_personal_page": self.update_your_personal_page,
            "send_a_fundraising_email": self.send_a_fundraising_email,
            "raise_your_first_donation": self.raise_your_first_donation,
            "recruit_a_team_member": self.recruit_a_team_member,
            "share_on": self.share_on,
            "steps": self.steps,
        }
        return walthrough


class Donors(db.Model):
    __tablename__ = "Donors"
    __schema__ = "donors"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    donor_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    city = db.Column(db.String(255))
    country = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    classification = db.Column(UUID(as_uuid=True), nullable=True)
    dedication = db.Column(UUID(as_uuid=True), nullable=True)
    donate_to = db.Column(
        ENUM("event", "team", "participant", name="donate_to", create_type=False, ),
        nullable=False,
    )
    transactions = db.relationship(
        "Transactions", backref="Donors", lazy=True, cascade="all,delete",
    )
    email_permission = db.Column(db.Boolean)
    show_donation_amount = db.Column(db.Boolean)
    show_donation_name = db.Column(db.Boolean)
    donated_on = db.Column(db.DateTime, nullable=False, default=func.now())

    def __init__(
            self,
            first_name,
            last_name,
            address,
            city,
            country,
            phone_number,
            classification,
            dedication,
            donate_to,
            email_permission,
            show_donation_name,
            show_donation_amount,
    ):
        self.first_name = first_name
        self.last_last = last_name
        self.address = address
        self.city = city
        self.country = country
        self.phone_number = phone_number
        self.classification = classification
        self.dedication = dedication
        self.donate_to = donate_to
        self.email_permission = email_permission
        self.show_donation_name = show_donation_name
        self.show_donation_amount = show_donation_amount

    def to_dict(self):
        donor_data = {
            "donor_id": self.donor_id,
            "first_name": self.first_name,
            "last_last": self.last_name,
            "address": self.address,
            "city": self.city,
            "country": self.country,
            "phone_number": self.phone_number,
            "classification": self.classification,
            "dedication": self.dedication,
            "donate_to": self.donate_to,
            "email_permission": self.email_permission,
            "show_donation_name": self.show_donation_name,
            "show_donation_amount": self.show_donation_amount,
        }
        return donor_data


class TwitterConnection(db.Model):
    __tablename__ = "TwitterConnection"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    twitter_connect_Id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id = db.Column(UUID(as_uuid=True), primary_key=True)
    twitter_key = db.Column(db.String(255))
    twitter_secret = db.Column(db.String(255))
    connnected_on = db.Column(db.DateTime, default=func.now())

    def __init__(self, user_id, twitter_key, twitter_secret):
        self.user_id = user_id
        self.twitter_key = twitter_key
        self.twitter_secret = twitter_secret

    def to_dict(self):
        twitter_data = {
            "user_id": dict(session).get("profile", None),
            "twitter_key": self.twitter_key,
            "twitter_secret": self.twitter_secret,
        }
        return twitter_data
    
    
    
    

class P2PFundraiser(db.Model):
    __tablename__ = "P2PFundraiser"
    organization_id = db.Column(db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    p2p_id = db.Column(db.String(255), nullable=True)
    campaign = db.Column(db.String(255), nullable=True)
    designation = db.Column(db.String(255), nullable=True)
    display_name = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    goal = db.Column(db.String(255), nullable=True)
    currency = db.Column(db.String(255), nullable=True)
    offline_amount = db.Column(db.String(255), nullable=True)
    offline_donation = db.Column(db.String(255), nullable=True)
    goal_date = db.Column(db.Date, nullable=True)
    personal_message = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), default="active", nullable=True)
    supporter = db.Column(db.String(255), nullable=True)
    profile_photo = db.Column(db.Text(), nullable=True)
    created_on = db.Column(db.DateTime, server_default=func.now())
    def __init__(
        self, 
        p2p_id,
        campaign,
        designation,
        display_name,
        first_name,
        last_name,
        email,
        goal,
        currency,
        offline_amount,
        offline_donation,
        goal_date,
        personal_message,
        supporter,
        organization_id,
        profile_photo=None,
        status=None,
        created_on=None,
        ):
        self.p2p_id = p2p_id
        self.campaign = campaign
        self.designation = designation
        self.display_name = display_name
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.goal = goal
        self.currency = currency
        self.offline_amount = offline_amount
        self.offline_donation = offline_donation
        self.goal_date = goal_date
        self.personal_message = personal_message
        self.organization_id = organization_id
        self.status = status
        self.supporter = supporter
        self.profile_photo = profile_photo
        self.created_on = created_on
    
    def __repr__(self):
        return "<P2P %r>" % self.display_name