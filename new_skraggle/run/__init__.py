import os

from celery import Celery
from flask import Flask
from flask_caching import Cache
from src.library.utility_classes.mail import Mail as MailClass

app = Flask(__name__)

app.config.from_object("src.app_config.Config")

if bool(os.getenv("REDIS_ENABLED")):
    cache = Cache(app, config={"CACHE_TYPE": "redis"})
    cache.init_app(app)

celery = Celery(app.name)
celery.conf.broker_url = app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379')
celery.conf.result_backend = app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

@celery.task(name='send_mail_in_background')
def send_mail_in_background(mail_options: dict = None):
    if not mail_options:
        print('No mail_options')
        return

    print('** Sending email in background **')
    print('** mail_options :>> **')
    print(mail_options)
    with app.app_context():
        mail_obj = MailClass(
            **mail_options,
            app=app
        )
        try:
            mail_obj.send()
        except Exception as e:
            print(e)