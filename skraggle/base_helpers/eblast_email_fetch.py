from skraggle.config import db
from skraggle.contact.models import ContactUsers, SegmentUsers, TagUsers


def contact_extract_emails(table, org_id, exclude=None):
    if exclude:
        _user_emails = list(
            set(
                [
                    email[0]
                    for email in db.session.query(table.primary_email)
                    .filter_by(organization=org_id)
                    .filter(table.id.in_(exclude))
                    .all()
                ]
            )
        )
        return _user_emails
    _user_emails = list(
        set([email[0] for email in db.session.query(table.primary_email).all()])
    )

    return _user_emails


def segment_extract_emails(segment_id, org_id, exclude=None):
    segment = SegmentUsers.query.filter_by(
        segment_id=segment_id, organization_id=org_id
    ).first()
    if exclude and segment:
        _user_emails = list(
            set(
                [
                    email[0]
                    for email in db.session.query(ContactUsers.primary_email)
                    .filter_by(organization_id=org_id)
                    .filter(ContactUsers.id.in_(exclude))
                    .all()
                ]
            )
        )
        return _user_emails

    if segment:
        contacts_list = list(map(str, segment.contacts))

        _user_emails = list(
            set(
                [
                    email[0]
                    for email in db.session.query(ContactUsers.primary_email)
                    .filter_by(organization_id=org_id)
                    .filter(ContactUsers.id.in_(contacts_list))
                    .all()
                ]
            )
        )
        return _user_emails


# segment_extract_emails('7a91b4f7-615a-49a5-b995-bff1ab154da3','ORG-KEYH5GfUzjJqNAMuj7GETc')


def tag_extract_emails(tag_id, org_id, exclude=None):
    tag = TagUsers.query.filter_by(tag_id=tag_id, organization_id=org_id).first()
    if exclude and tag:
        _user_emails = list(
            set(
                [
                    email[0]
                    for email in db.session.query(ContactUsers.primary_email)
                    .filter_by(organization_id=org_id)
                    .filter(ContactUsers.id.in_(exclude))
                    .all()
                ]
            )
        )
        return _user_emails

    if tag:
        contacts_list = list(map(str, tag.contacts))

        _user_emails = list(
            set(
                [
                    email[0]
                    for email in db.session.query(ContactUsers.primary_email)
                    .filter_by(organization_id=org_id)
                    .filter(ContactUsers.id.in_(contacts_list))
                    .all()
                ]
            )
        )
        return _user_emails


def extract_email(_content, exclude, org_id):
    if _content.eblast_users == "contacts":
        _user_emails = contact_extract_emails(ContactUsers, org_id)
        if exclude:
            _all_emails = set(contact_extract_emails(ContactUsers, org_id))
            _exclude_emails = set(
                contact_extract_emails(
                    ContactUsers, org_id, exclude=_content._exclude_emails
                )
            )
            _user_emails = [_all_emails.symmetric_difference(_exclude_emails)]
            return _user_emails
        return _user_emails

    elif _content.eblast_users == "segment":
        _user_emails = segment_extract_emails(_content.segment_id, org_id)
        if exclude:
            _all_emails = set(segment_extract_emails(_content.segment_id, org_id))
            _exclude_emails = set(
                segment_extract_emails(
                    _content.segment_id, org_id, exclude=_content._exclude_emails
                )
            )
            _user_emails = [_all_emails.symmetric_difference(_exclude_emails)]
            return _user_emails
        return _user_emails

    elif _content.eblast_users == "tags":
        _user_emails = tag_extract_emails(_content.tag_id, org_id)
        if exclude:
            _all_emails = set(tag_extract_emails(_content.tag_id, org_id))
            _exclude_emails = set(
                tag_extract_emails(
                    _content.tag_id, org_id, exclude=_content._exclude_emails
                )
            )
            _user_emails = [_all_emails.symmetric_difference(_exclude_emails)]
            return _user_emails
        return _user_emails


def email_extracter(table, col_name):
    _emails = list(
        set([email[0] for email in db.session.query(getattr(table, col_name)).all()])
    )
    return _emails
