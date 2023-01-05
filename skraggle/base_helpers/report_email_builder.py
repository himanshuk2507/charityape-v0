from flask_mail import Message
from datetime import datetime


def get_expire_days(expire_date):
    return (abs(expire_date - datetime.now())).days


def prepare_email_message(emails):
    report_message_types = {
        "expiring_soon": Message(
            "Your Subscription Gonna Expire Soon..!!", recipients=[emails]
        ),
        "active_members": Message("Thank you for your Support. ", recipients=[emails]),
        "lybunt_users": Message("We welcome donations ", recipients=[emails]),
        "sybunt_users": Message("We need your support", recipients=[emails]),
        "elapsed_memberships": Message("Elapsed Memberships", recipients=[emails]),
        "inactive_volunteers": Message("Inactive Volunteers", recipients=[emails]),
        "active_volunteers": Message("Active Volunteers", recipients=[emails]),
        "outstanding_pledges": Message("outstanding_pledges", recipients=[emails]),
    }
    return report_message_types


def prepare_email_body():
    report_body_types = {
        "expiring_soon": "Renew Your subscription",
        "active_members": "Thank you for your support",
        "lybunt_users": "Support Us",
        "sybunt_users": "Support Us",
        "elapsed_memberships": "Support Us",
        "inactive_volunteers": "Support Us",
        "active_volunteers": "Thank you for your support",
        "outstanding_pledges": "Sorry to inform you",
    }
    return report_body_types


def prepare_email_html(name, expire_date):
    report_html_types = {
        "expiring_soon": (
            f"<p>Hi {name},</p> \r\n <p>Your membership  is about to expire on <strong> {expire_date.strftime('%d %B, %Y') if expire_date else None} </strong> "
            f"\r\n <p> Remaining Days Left : {get_expire_days(expire_date) if expire_date else None} </p>"
            f"We hope you&rsquo;ve enjoyed [benefits of your membership].</p> \r\n<p>Good news! There&rsquo;s still "
            f"time to renew, and it&rsquo;s as easy as ever &ndash; just click the link below to renew your "
            f"membership \r\n <a href = 'http://127.0.0.1:5000/memberships/all' > \r\n <p>RENEW "
            f"NOW</p></a>\r\n<p>Thanks..</p> "
        ),
        "active_members": (
            f"<p>Hi {name},</p> \r\n <p>Thank you so much for continually supporting us "
            f"..\r\n<p>Thanks..</p> "
        ),
        "lybunt_users": (
            f"<p>Hi {name},</p> \r\n <p>We welcome donations from our users to support all the work we’re "
            f"doing!\r\n<p>Thanks..</p> "
        ),
        "sybunt_users": (
            f"<p>Hi {name},</p> \r\n <p>It's been a long time ,We welcome donations from our users to "
            f"support all the work we’re doing!\r\n<p>Thanks..</p> "
        ),
        "elapsed_memberships": (
            f"<p>Hi {name},</p> \r\n <p>It's been a long time ,We welcome donations from our users to "
            f"support all the work we’re doing!\r\n<p>Thanks..</p> "
        ),
        "inactive_volunteers": (
            f"<p>Hi {name},</p> \r\n <p>It's been a long time ,We welcome donations from our users to "
            f"support all the work we’re doing!\r\n<p>Thanks..</p> "
        ),
        "active_volunteers": (
            f"<p>Hi {name},</p> \r\n <p>thanks for supporting us "
            f"We have new updates!\r\n<p>Thanks..</p> "
        ),
        "outstanding_pledges": (
            f"<p>Hi {name},</p> \r\n <p>thanks for supporting us "
            f"There is a Pledge you promised has been late by  <strong>{get_expire_days(expire_date) if expire_date else None}</strong> Days\r\n<p>Hope you check "
            f"it out ,Thanks..</p> "
        ),
    }
    return report_html_types
