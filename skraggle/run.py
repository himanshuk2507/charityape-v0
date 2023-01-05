import os

from celery import Celery
from flask import Flask
from flask_mail import Mail
from flask_caching import Cache
from flask_cors import CORS
from redis import Redis
import rq

app = Flask(__name__)
CORS(app)

app.config.from_object("skraggle.config.Config")

if bool(os.getenv("REDIS_ENABLED")):
    cache = Cache(app, config={"CACHE_TYPE": "redis"})
    cache.init_app(app)

celery = Celery(
    app.name,
    broker=app.config["CELERY_BROKER_URL"],
    include=["base_helpers.eblast_sender"],
)
celery.conf.update(app.config, broker=app.config['CELERY_BROKER_URL'])
mail = Mail(app)