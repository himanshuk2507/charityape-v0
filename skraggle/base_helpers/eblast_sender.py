from skraggle.base_helpers.responser import DataResponse
from skraggle.run import mail, celery, app
from flask_mail import Message


@celery.task(name="eblast_send")
def eblast_send(
    recipients: list,
    sender: str,
    subject: str,
    content: str,
    attachments=None,
    reply_to=None,
):

    try:
        with app.app_context():
            msg = Message(
                subject, sender=sender, reply_to=reply_to, recipients=recipients,
            )
            msg.body = "testing"
            msg.html = content
            mail.send(msg)
            return True
    except Exception as e:
        return str(e)
