from pathlib import Path
import os

from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_sqlalchemy import SQLAlchemy
from sendgrid import SendGridAPIClient
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import Query
import socket

basedir = Path(__file__).parent.parent
load_dotenv(basedir / '.env')
upload_dir = os.path.join(basedir, "attachments")
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "docx"}
DATABASE_URI = os.getenv("DATABASE_URI") or "postgresql://postgres:postgres@database/postgres"

class OrgFilterQuery(Query):
    def all(self):
        org_id = None
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            org_id = claims["org"]
        except Exception:
            pass

        return (
            self.limit(None)
            .offset(None)
            .filter_by(organization_id=org_id)
            ._iter()
            .all()
        )


db = SQLAlchemy(query_class=OrgFilterQuery)
engine = create_engine(
    DATABASE_URI
)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class Config(object):
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    UPLOAD_FOLDER = "attachments"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEST_TRUE = True
    FLASK_ENV = "development"
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = True
    SESSION_PERMANENT = True
    DB_NAME = os.environ.get("DB_NAME")
    HEROKU_DB_USERNAME = os.getenv("HEROKU_DB_USERNAME")
    HEROKU_DB_PASSWORD = os.getenv("HEROKU_DB_PASSWORD")
    HEROKU_DB_NAME = os.getenv("HEROKU_DB_NAME")
    HEROKU_HOST = os.getenv("HEROKU_HOST")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = True
    SENDGRID_MAIL = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ORGANIZATION_ID = "ORG_SUPER_SECRET@012345"
    ENC_KEY = os.getenv("ENC_KEY")
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL") or 'redis://'
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    RELEASE_LEVEL = (
        os.getenv("RELEASE_LEVEL") if "RELEASE_LEVEL" in os.environ else "local"
    )

    host = str(socket.gethostname())
    if RELEASE_LEVEL:
        # local = "local" in host or host.startswith("192.") or host.startswith("127.")
        if RELEASE_LEVEL == "local" or RELEASE_LEVEL == "stage" or RELEASE_LEVEL == "prod":
            SQLALCHEMY_DATABASE_URI = (
                DATABASE_URI
            )
        else:
            raise ValueError("Invalid or Malformed release level")
    else:
        raise ValueError("Release level not set")

    print("Host serving the application =>", host)
    print("SQL_ALCHEMY_CONNECTION string =>", SQLALCHEMY_DATABASE_URI)
    print(f"Environment and Database successfully configured for {RELEASE_LEVEL}")
