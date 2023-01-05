from src.app_config import db
from src.mail_blasts.models import MailBlast
from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.campaigns.fixtures import CampaignFixture
from src.tests.integration.contacts.fixtures import ContactUsersFixture, ContactCompaniesFixture


class MailBlastFixture:
    '''
    Creates a MailBlast object for testing with.
    :param data: (optional) dict[str, Any] with fields from MailBlasts
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        data["organization_id"] = AdminFixture().admin.organization_id
        mail_blast: MailBlast = MailBlast(**data)

        db.session.add(mail_blast)
        db.session.flush()
        db.session.commit()

        self.mail_blast = mail_blast
        self.id = mail_blast.id

    @classmethod
    def default_obj(cls):
        campaign_id = CampaignFixture().id
        contact_id = ContactUsersFixture().id
        company_id = ContactCompaniesFixture().id

        return dict(contact_id=contact_id, name="My mailing list", company_id=company_id,
                    category="newsletter", email_from="me@me.com", email_to=["fefofef479@runqx.com"],
                    email_subject="Happy New Month!", email_body="Dear world, Hello and bye.",
                    tags=[], opened_by=[], recipients=[], is_draft=False, reply_to=[],
                    email_sender_name=None,
                    campaign_id=campaign_id
                    )
