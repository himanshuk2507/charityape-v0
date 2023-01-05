from flask import url_for, redirect, request, session
from skraggle.base_helpers import crypter
from skraggle.contact.models import GoogleUsers
from flask.globals import current_app
from flask_cors import CORS
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
import os
from flask_jwt_extended import JWTManager

from skraggle.integrations.neoncrm_connect import neoncrmconnect
from skraggle.integrations.salesforce_connect import salesforceconnect
from skraggle.donor_portal.donor_fundraisers import donorportalfund
from skraggle.globalhelpers.global_endpoints import globalendpoints
from skraggle.marketing_keys.views import marketingviews

# from reports.calculations import ContactCalculationsView
from skraggle.reports.calculations import DonationCalculationsView, TransactionCalculationsView
from skraggle.reports.transaction_reports import transactionreportviews
from skraggle.run import app, mail
from skraggle.eblasts.eblasts import eblastsview
import threading
from flask_login import LoginManager
from skraggle.profile.profile import adminprofile
from skraggle.validators_logics.validators import EmailListValidator
from skraggle.config import db
from skraggle.base_helpers.responser import DataResponse
from flask_mail import Message
from skraggle.contact.contacts import contactview
from skraggle.contact.company import companyview
from skraggle.contact.households import householdview
from skraggle.contact.tags import tagview
from skraggle.dashboard.widgets import widgetview
from skraggle.contact.segments import segmentview
from skraggle.contact.profile_tab.profile_tab import profiletab
from skraggle.contact.todo_tab.todo_tab import todotab
from skraggle.contact.interaction_tab.interaction_tab import interactiontab
from skraggle.contact.volunteering_tab.volunteering_tab import volunteertab
from skraggle.contact.Fundraising.transactions import transactiontab
from skraggle.decarotor import login_required
from skraggle.donation.pledges import pledges
from skraggle.donation.paypal_handler import paymenthandler
from skraggle.donation.kpis import kpiview
from skraggle.forms.form import formview
from skraggle.contact.memberships.memberships import membershipview
from skraggle.forms.url_shortener import urlshortiew
from skraggle.forms.donation_setup import donationsetupiew
from skraggle.donation.stripe_handler import stripehandler
from skraggle.donation.schedule_recurring_donations import schedule_recurring_donations
from skraggle.donation.schedule_recurring_revenue import schedule_recurring_revenues
from skraggle.donation.transaction_donation import transactions_donation
from skraggle.donation.transaction_revenue import transaction_revenues
from skraggle.donation.association import associationviews
from skraggle.donation.admin import adminview
from skraggle.campaigns.campaign import campaignviews
from skraggle.p2p.myEvents.events import eventviews
from skraggle.p2p.peer_to_peer import peertopeer
from skraggle.p2p.myEvents.classification import classificationviews
from skraggle.p2p.myEvents.categories import categoryviews
from skraggle.p2p.myEvents.promocodes import promocodeviews
from skraggle.p2p.myEvents.dedication import dedicationviews
from skraggle.p2p.myEvents.donation_amount import donationamountviews
from skraggle.p2p.myEvents.restriction import restrictionviews
from skraggle.p2p.constituents.teams import p2pteams
from skraggle.p2p.constituents.p2p_participants import p2pparticipants
from skraggle.p2p.content.badges import p2pbadges
from skraggle.p2p.store.categories import storecategoryviews
from skraggle.p2p.constituents.donors import p2pdonors
from skraggle.p2p.store.products import storeproductsviews
from pydantic import ValidationError
from skraggle.p2p.content.sponsor_categories import sponsorcategoriesviews
from skraggle.events.event.eventInformation import eventinfoviews
from skraggle.events.event.eventSettings import eventsettingsviews
from skraggle.events.event.eventRegistrationReceipt import eventregisterationrecieptviews
from skraggle.events.packages import packageviews
from skraggle.events.fields import fieldviews
from skraggle.events.promocodes import promocodeview
from skraggle.landing_page.landing_page import elementsviews
from skraggle.p2p.share_your_event.connect_twitter import twitterconnect
from skraggle.p2p.share_your_event.connect_facebook import facebookconnect
from skraggle.p2p.share_your_event.social_sharing_settings import socialsettings
from skraggle.donation.plaid_handler import plaidhandler
from skraggle.other_funcs.new_user_onboarding import newuseronboard
from skraggle.profile.models import Admin, AccessTokenBlocklist
from skraggle.profile.email_confirmation import confirmemail
from skraggle.reports.custom_reports import customreports
from skraggle.profile.twofactor import twofasecurity
from skraggle.profile.organization_settings import orgsettings
from skraggle.profile.invite_and_teams import invitationview
from skraggle.donor_portal.donorportal_settings import donorportalsettings
from skraggle.donor_portal.donorportal_views import donorportalviews
from skraggle.p2p.myEvents.event_information import eventinformationviews
from celery import Celery
from skraggle.utils.background_workers.blueprint import initialize_workers, workers


# from reports.calculations import reportcalculations
# common
app.config.from_object("skraggle.config.Config")
CORS(app, resources={f"/*": {"origins": "*"}})
login_manager = LoginManager()
login_manager.init_app(app)
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_token, jwt_payload):
    jti = jwt_payload["jti"]
    token = db.session.query(AccessTokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id)


db.init_app(app)
oauth = OAuth(app)


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
migrate = Migrate(compare_type=True)
migrate.init_app(app, db)

# import Models


# blueprints registering
app.register_blueprint(contactview, url_prefix="/contacts")
app.register_blueprint(companyview, url_prefix="/company")
app.register_blueprint(householdview, url_prefix="/households")
app.register_blueprint(tagview, url_prefix="/tags")
app.register_blueprint(widgetview, url_prefix="/dashboard")
app.register_blueprint(segmentview, url_prefix="/segments")
app.register_blueprint(profiletab, url_prefix="/contacts/profile")
app.register_blueprint(interactiontab, url_prefix="/interactions")
app.register_blueprint(transactiontab, url_prefix="/transactions")
app.register_blueprint(todotab, url_prefix="/contacts/todos")
app.register_blueprint(volunteertab, url_prefix="/contacts/volunteer")
app.register_blueprint(confirmemail, url_prefix="/email")
app.register_blueprint(pledges, url_prefix="/pledges")
app.register_blueprint(paymenthandler, url_prefix="/payments")
app.register_blueprint(kpiview, url_prefix="/donations")
app.register_blueprint(formview, url_prefix="/forms")
app.register_blueprint(adminprofile, url_prefix="/admin")
app.register_blueprint(donationsetupiew, url_prefix="/donation_setup")
app.register_blueprint(stripehandler, url_prefix="/payments")
app.register_blueprint(
    schedule_recurring_donations, url_prefix="/donations/recurring"
)
app.register_blueprint(
    schedule_recurring_revenues, url_prefix="/schedule-recurring-revenues"
)
app.register_blueprint(transactions_donation, url_prefix="/transaction-donations")
app.register_blueprint(transaction_revenues, url_prefix="/transaction-revenues")
app.register_blueprint(associationviews, url_prefix="/association-views")
app.register_blueprint(campaignviews, url_prefix="/campaigns")
app.register_blueprint(urlshortiew, url_prefix="")
app.register_blueprint(eventviews, url_prefix="/p2p-events")
app.register_blueprint(peertopeer, url_prefix="/peertopeer")
app.register_blueprint(classificationviews, url_prefix="/p2p-classification")
app.register_blueprint(categoryviews, url_prefix="/p2p-category")
app.register_blueprint(promocodeviews, url_prefix="/p2p-promocodes")
app.register_blueprint(dedicationviews, url_prefix="/p2p-dedication")
app.register_blueprint(donationamountviews, url_prefix="/p2p-donationamount")
app.register_blueprint(restrictionviews, url_prefix="/p2p-restriction")
app.register_blueprint(p2pteams, url_prefix="/p2p-teams")
app.register_blueprint(p2pparticipants, url_prefix="/p2p-participants")
app.register_blueprint(p2pdonors, url_prefix="/p2p-donors")
app.register_blueprint(p2pbadges, url_prefix="/p2p-badges")
app.register_blueprint(storecategoryviews, url_prefix="/p2p-storecategory")
app.register_blueprint(storeproductsviews, url_prefix="/p2p-storeproduct")
app.register_blueprint(eblastsview, url_prefix="/eblasts")
app.register_blueprint(
    sponsorcategoriesviews, url_prefix="/p2p-content-sponsorcategories"
)
app.register_blueprint(eventinfoviews, url_prefix="/event-info")
app.register_blueprint(eventsettingsviews, url_prefix="/event-setting")
app.register_blueprint(
    eventregisterationrecieptviews, url_prefix="/event-registerreceipt"
)
app.register_blueprint(packageviews, url_prefix="/event-package")
app.register_blueprint(membershipview, url_prefix="/memberships")
app.register_blueprint(fieldviews, url_prefix="/event-fields")
app.register_blueprint(promocodeview, url_prefix="/event-promocode")
app.register_blueprint(twitterconnect, url_prefix="/twitter")
app.register_blueprint(facebookconnect, url_prefix="/facebook")
app.register_blueprint(elementsviews, url_prefix="/element")
app.register_blueprint(socialsettings, url_prefix="/p2p-social-share")
app.register_blueprint(newuseronboard, url_prefix="/new_user_onboarding")
app.register_blueprint(plaidhandler, url_prefix="/payments")
app.register_blueprint(customreports, url_prefix="/reports")
app.register_blueprint(marketingviews, url_prefix="/marketing")
app.register_blueprint(twofasecurity, url_prefix="/2fa")
app.register_blueprint(orgsettings, url_prefix="/organization")
app.register_blueprint(invitationview, url_prefix="/invitation")
app.register_blueprint(globalendpoints, url_prefix="/global")
app.register_blueprint(donorportalsettings, url_prefix="/donor-portal")
app.register_blueprint(donorportalviews, url_prefix="/donor-portal")
app.register_blueprint(donorportalfund, url_prefix="/donor-portal")
app.register_blueprint(eventinformationviews, url_prefix="/p2p-event-information")
app.register_blueprint(salesforceconnect, url_prefix="/salesforce")
app.register_blueprint(transactionreportviews, url_prefix="/reports/transactions")
app.register_blueprint(neoncrmconnect, url_prefix="/neoncrm")
app.register_blueprint(adminview, url_prefix="/donations")
# background workers
app.register_blueprint(workers)

# Flask Views
# ContactCalculationsView.register(app)
DonationCalculationsView.register(app, route_base="/reports/calculations")
TransactionCalculationsView.register(app, route_base="/reports/calculations")
# End Flask Registering

# Google Oauth Config
CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    # This is only needed if using openId to fetch user info
    client_kwargs={"scope": "openid email profile"},
)


def eblaster(msg):
    # msg = Message("Twilio SendGrid Test Email", recipients=emails)
    # msg.body = body
    # msg.html = subject
    try:
        mail.send(msg)
        resp = DataResponse(True, "Message sent Successfully")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()


"""
# Api to send emails to list of emails 
@parameters : "emails" seperated by comma 
Ex: http:domain.com/eblasts/send_email/emails=email1@gmail.com, email2@gmail.com,email3@gmail.com
"""


@app.route("/eblasts/send_eblasts", methods=["GET"])
def email_blaster():
    emails_list = request.form["emails"]
    body = request.form["body"]
    subject = request.form["subject"]
    emails = list(set(list(map(str, emails_list.split(",")))))
    try:
        valid = EmailListValidator(emails=emails)
        if valid:
            app = current_app
            with app.app_context():
                msg = Message(subject, recipients=emails)
                msg.body = body
                msg.html = subject
                threading.Thread(target=mail.send(msg)).start()
            resp = DataResponse(True, "Email Sent Successfully to all Eblasts")
            return resp.status()
    except ValidationError as e:
        return e.json()


@app.route("/")
@login_required
def home():
    email = dict(session)["profile"]["email"]
    return f"Hello, you are logged in as {email}!"


@app.route("/login")
def login():
    google = oauth.create_client("google")  # create the google oauth client
    redirect_uri = url_for("authorize", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/login/callback")
def authorize():
    google = oauth.create_client("google")  # create the google oauth client
    token = (
        google.authorize_access_token()
    )  # Access token from google (needed to get user info)
    resp = google.get("userinfo")  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = GoogleUsers.query.filter_by(google_id=user_info.get("id")).first()
    if not user:
        saveusers = GoogleUsers(
            google_id=user_info.get("id"),
            fullname=user_info.get("name"),
            fname=user_info.get("given_name"),
            lname=user_info.get("family_name"),
            email=user_info.get("email"),
            is_verified=user_info.get("verified_email"),
            location=user_info.get("locale"),
        )
        db.session.add(saveusers)
        db.session.commit()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session["profile"] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect("/")


@app.route("/logout")
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect("/")

initialize_workers()

if __name__ == "__main__":

    # Shut down the scheduler when exiting the app
    app.run(debug=True, host="0.0.0.0", port=80)
