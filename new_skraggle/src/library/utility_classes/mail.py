from typing import List

from flask_mail import Message, Mail as FlaskMail, Attachment

from src.app_config import Config

class MailAttachment:
    def __init__(self, filename='file', encoding=None, file_path=None):
        if not encoding or not file_path:
            return

        self.filename = filename 
        self.encoding = encoding
        self.file_path = file_path

        with open(file_path, "rb") as file:
            self.file = file
        return



class Mail:
    def __init__(
        self, app=None, subject='', recipients: List[str] = None, text: str=None, html: str=None, attachments: List[MailAttachment]=None,
        sender: str = None, reply_to: str = None
    ):
        '''
        Create a Mail object that can be used to handle in-app mailing
        '''

        if not app:
            return
        mail_handler = FlaskMail(app)

        self.subject = subject
        self.recipients = recipients
        self.text = text
        self.html = html
        self.attachments: List[MailAttachment] = attachments
        self.sender = sender or Config.MAIL_DEFAULT_SENDER
        self.reply_to = reply_to or self.sender

        self.mail_handler = mail_handler

    def send(self):
        if not self.recipients:
            return False, '`recipients` must be defined'

        msg = Message(
            subject=self.subject,
            body=self.text,
            html=self.html,
            attachments=self.attachments,
            recipients=self.recipients,
            sender=self.sender,
            reply_to=self.reply_to
        )
        self.msg = msg 

        try:
            self.compile_attachments()
            self.mail_handler.send(msg)
            return True, None
        except Exception as e:
            return False, e
    
    def compile_attachments(self):
        if not self.attachments:
            return False
        for attachment in self.attachments:
            self.msg.attach(
                attachment.filename,
                attachment.encoding,
                attachment.file
            )
        return True