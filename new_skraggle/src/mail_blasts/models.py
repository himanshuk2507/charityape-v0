from datetime import datetime, timedelta
from operator import and_
from typing import List
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from celery.utils import gen_unique_id
from celery.result import AsyncResult
from run import send_mail_in_background

from src.app_config import ModelMixin, OrganizationMixin, db
from src.campaigns.models import Campaign
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.contacts.interactions.models import ContactInteraction
from src.library.base_helpers.date_manipulation import hours_between_dates
from src.library.base_helpers.file_manipulation import download_file, get_filename_from_path
from src.library.html_templates.mail_blast_template import MailBlastTemplate
from src.library.utility_classes.mutable_list import MutableList


class MailBlast(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'MailBlast'

    name = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)

    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactUsers.id'), nullable=True)
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactCompanies.id'), nullable=True)
    
    campaign_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Campaign.id'), nullable=True)

    email_to = db.Column(ARRAY(db.String(255)), nullable=False, default=[])
    email_from = db.Column(db.String(255), nullable=True)
    email_subject = db.Column(db.String(255), nullable=True)
    email_sender_name = db.Column(db.String(255), nullable=True)
    email_body = db.Column(db.Text, nullable=True)
    email_attachments = db.Column(ARRAY(db.String(255)), nullable=False, default=[])
    send_to_all_contacts = db.Column(db.Boolean, nullable=False, default=True)

    send_at = db.Column(db.DateTime, nullable=True)

    archived = db.Column(db.Boolean, nullable=False, default=False)
    unsubscribe_message = db.Column(db.Text, nullable=True)
    allow_custom_feedback_on_unsubscribe = db.Column(db.Boolean, nullable=False, default=False)

    worker_task_id = db.Column(db.String(255), nullable=True)
    is_draft = db.Column(db.Boolean, nullable=False, default=False)

    tags = db.Column(MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=False, default=[])
    opened_by = db.Column(MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=False, default=[])
    recipients = db.Column(MutableList.as_mutable(ARRAY(db.String(255))), nullable=False, default = [])
    reply_to = db.Column(MutableList.as_mutable(ARRAY(db.String(255))), nullable=False, default = [])


    def __init__(
        self, name = None, category = None, contact_id = None, company_id = None,
        campaign_id = None, email_from = None, email_to = None,
        email_subject = None, email_body = None, send_at = None, 
        archived = False, unsubscribe_message = None, 
        allow_custom_feedback_on_unsubscribe = False, worker_task_id = None,
        tags = [], opened_by = [], recipients = [], is_draft = False, reply_to = [],
        email_sender_name = None, email_attachments = [],
        organization_id = None,
    ):
        self.name = name
        self.category = category
        
        self.contact_id = contact_id
        
        self.company_id = company_id
        
        self.campaign_id = campaign_id
        
        self.email_from = email_from
        self.email_sender_name = email_sender_name
        self.email_subject = email_subject
        self.email_body = email_body
        self.email_to = email_to
        
        self.send_at = send_at
        
        self.archived = archived
        self.unsubscribe_message = unsubscribe_message
        self.allow_custom_feedback_on_unsubscribe = allow_custom_feedback_on_unsubscribe

        self.worker_task_id = worker_task_id
        self.tags = tags or []
        self.opened_by = opened_by or []
        self.recipients = recipients or []
        self.is_draft = is_draft
        self.reply_to = reply_to or []
        self.email_attachments = email_attachments or []
        
        self.organization_id = organization_id


    def schedule_blast(self):
        '''
        Schedule this blast in a background worker.
        If this blast has already been scheduled, cancel the scheduled task and create a new one.
        '''
        if not self.send_at or not self.email_body or not self.email_subject or self.is_draft == True:
            return
        
        now = datetime.utcnow()

        if now > self.send_at:
            # can't schedule a mailblast in the past
            print('skipping schedule_blast(): now > send_at')
            return

        if self.worker_task_id:
            # if a mailblast has been scheduled before, cancel it
            AsyncResult(self.worker_task_id).revoke()
        
        # assign a new task ID that can be used to keep track of this scheduled mailblast later
        self.worker_task_id = gen_unique_id()
        
        # Celery.apply_async has a timezone-related bug with the `eta` param
        # so we'll use `countdown`
        # `countdown` is the number of seconds left until self.send_at
        countdown = (self.send_at - now).total_seconds()

        recipients = self.get_recipients()
        self.recipients = recipients
        self.is_draft = False

        for email in recipients:
            contact: ContactUsers = ContactUsers.query.filter_by(primary_email=email, organization_id=self.organization_id).one_or_none()
            company: ContactCompanies = ContactCompanies.query.filter_by(email=email, organization_id=self.organization_id).one_or_none()
            if contact:
                interaction = ContactInteraction(
                    contact_id=contact.id,
                    is_individual=True,
                    type='email',
                    subject=self.email_subject,
                    attachments=self.email_attachments,
                    todos=None
                )
                contact.interactions.append(interaction)
            elif company:
                interaction = ContactInteraction(
                    company_id=company.id,
                    is_individual=False,
                    type='email',
                    subject=self.email_subject,
                    attachments=self.email_attachments,
                    todos=None
                )
                company.interactions.append(interaction)

        db.session.commit()
        
        send_mail_in_background.apply_async(
            countdown = countdown,
            task_id = self.worker_task_id,
            kwargs = {'mail_options': dict(
                html = MailBlastTemplate().render(email_body=self.email_body),
                text = self.email_body,
                recipients = recipients,
                subject = self.email_subject,
                sender = self.email_from,
                reply_to = self.reply_to[0] if len(self.reply_to) > 0 else self.email_from,
                attachments = [self.process_attachment(attachment) for attachment in self.email_attachments]
            )}
        )


    def process_attachment(self, url: str = None):
        file = download_file(url)
        if file is None:
            return None, None
        return file, get_filename_from_path(file)


    def update(self, data: dict = None):
        if not data:
            return False, 'No data was provided for update'
        
        organization_id = data.get('organization_id')
        
        old_campaign: Campaign = Campaign.fetch_by_id(
            id=self.campaign_id,
            organization_id=organization_id
        ) if self.campaign_id else None
        old_contact: ContactUsers = ContactUsers.fetch_by_id(
            id=self.campaign_id,
            organization_id=organization_id
        ) if self.contact_id else None
        old_company: ContactCompanies = ContactCompanies.fetch_by_id(
            id=self.campaign_id,
            organization_id=organization_id
        ) if self.company_id else None

        if data.get('campaign_id'):
            if old_campaign:
                old_campaign.mailblasts.remove(self)

            new_campaign: Campaign = Campaign.fetch_by_id(
                id=data.get('campaign_id'),
                organization_id=organization_id
            )
            if not new_campaign:
                return False, 'No campaign exists with this ID'

        assignee = data.get('assignee')

        if assignee:
            self.company_id = None
            self.contact_id = None
            
            new_contact: ContactUsers = ContactUsers.fetch_by_id(
                id=assignee,
                organization_id=organization_id
            )
            if new_contact:
                if old_contact:
                    old_contact.assigned_mailblasts.remove(self)
                new_contact.assigned_mailblasts.append(self)
                db.session.add(new_contact)
            else:
                new_company: ContactCompanies = ContactCompanies.fetch_by_id(
                    id=assignee,
                    organization_id=organization_id
                )
                if new_company:
                    if old_company:
                        old_company.mailblasts.remove(self)
                    new_company.assigned_mailblasts.append(self)
                else:
                    return False, "No contact found with this ID"

        db.session.commit()
        self.schedule_blast()
        
        return super().update(data)


    def get_recipients(self):
        if self.send_to_all_contacts == False:
            contacts: List[ContactUsers] = ContactUsers.query.filter(
                and_(
                    ContactUsers.is_subscribed_to_mailblasts == True,
                    ContactUsers.primary_email.in_(self.email_to)
                )
            ).all()
            companies: List[ContactCompanies] = ContactCompanies.query.filter(
                and_(
                    ContactCompanies.is_subscribed_to_mailblasts == True,
                    ContactCompanies.primary_email.in_(self.email_to)
                )
            ).all()
            return [contact.primary_email for contact in contacts] + [company.email for company in companies]
        
        contacts: List[ContactUsers] = ContactUsers.query.filter(
            ContactUsers.is_subscribed_to_mailblasts == True,
        ).all()
        companies: List[ContactCompanies] = ContactCompanies.query.filter(
            ContactCompanies.is_subscribed_to_mailblasts == True,
        ).all()
        return [contact.primary_email for contact in contacts] + [company.email for company in companies]

    
    def get_mailing_list(self):
        recipients = self.get_recipients()
        return ContactUsers.query.filter(
            and_(
                ContactUsers.organization_id == self.organization_id,
                ContactUsers.primary_email.in_(recipients)
            )
        ).all() + \
            ContactCompanies.query.filter(
                and_(
                    ContactCompanies.organization_id == self.organization_id,
                    ContactCompanies.email.in_(recipients)
                )
            ).all()


    def get_assignee(self):
        contact = self.contact_id or self.company_id
        if not contact:
            return None
        filter_params = dict(
            organization_id = self.organization_id,
            id = contact
        )
        return ContactUsers.query.filter_by(
            **filter_params
        ).one_or_none() or ContactCompanies.query.filter_by(
            **filter_params
        ).one_or_none()
    
    assignee = property(get_assignee)


    @classmethod
    def register(cls, data: dict = None):
        if not data:
            raise Exception('MailBlast.register() requires an argument for `data`')

        # validations
        required_fields = ['organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"
        
        assignee = data.get('assignee')
        if assignee:
            data.pop('assignee')
        mailblast: cls = cls(**data)
        organization_id = data.get('organization_id')
        
        if data.get('campaign_id'):
            campaign: Campaign = Campaign.fetch_by_id(
                id=data.get('campaign_id'),
                organization_id=organization_id
            )
            campaign.mailblasts.append(mailblast)
            db.session.add(campaign)
        
        if assignee:
            contact: ContactUsers = ContactUsers.fetch_by_id(
                id = assignee,
                organization_id = organization_id
            )
            if contact:
                contact.assigned_mailblasts.append(mailblast)
                mailblast.contact_id = assignee
                db.session.add(contact)
            else:
                company: ContactCompanies = ContactCompanies.fetch_by_id(
                    id = assignee,
                    organization_id = organization_id
                )
                if company:
                    company.assigned_mailblasts.append(mailblast)
                    mailblast.company_id = assignee
                    db.session.add(company)

        db.session.add(mailblast)
        db.session.flush()
        db.session.commit()

        mailblast.schedule_blast()

        return True, mailblast