import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from flask_cors import CORS
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from run import app

from src.app_config import db

from src.profile.endpoints import admin_endpoints
from src.profile.payment_settings.stripe.endpoints import stripe_settings_endpoints
from src.profile.payment_settings.paypal.endpoints import paypal_settings_endpoints
from src.contacts.contact_users.endpoints import contacts_tab_endpoints
from src.contacts.households.endpoints import households_tab_endpoints
from src.contacts.tags.endpoints import contact_tags_tab_endpoints
from src.contacts.companies.endpoints import contact_companies_endpoints
from src.contacts.interactions.endpoints import contact_interactions_endpoints
from src.contacts.todos.endpoints import contacts_todos_endpoints
from src.contacts.volunteering.endpoints import contacts_volunteer_activity_endpoints
from src.campaigns.endpoints import campaign_tab_endpoints
from src.forms.endpoints import forms_tab_endpoints
from src.p2p.endpoints import p2p_endpoints
from src.events.event.endpoints import eventviews
from src.events.fields.endpoints import fieldviews
from src.events.package.endpoints import packageviews
from src.events.promocode.endpoints import promocode
from src.donations.pledges.endpoints import pledges_tab_endpoints
from src.elements.endpoints import elements_tab_endpoints
from src.mail_blasts.endpoints import mailblast_tab_endpoints
from src.donations.one_time_transactions.endpoints import one_time_transactions_tab_endpoints
from src.donations.sources.endpoints import donation_sources_endpoints
from src.donations.recurring_transactions.endpoints import recurring_transactions_tab_endpoints
from src.donations.kpis.endpoints import donation_kpis_tab_endpoints
from src.donations.summary.endpoints import donation_summary_tab_endpoints
from src.installments.endpoints import installments_endpoints
from src.keywords.endpoints import keyword_endpoints
from src.impact_area.endpoints import impact_area_endpoints
from src.reports.endpoints import reports_tab_endpoints
from src.integrations.eventbrite.endpoints import eventbrite

from src.profile.models import AccessTokenBlocklist, Admin
from src.library.custom_cli_commands import custom_cli_commands

# configure CORS headers
CORS(app, resources={f"/*": {"origins": "*"}})

login_manager = LoginManager()
login_manager.init_app(app)
jwt_manager = JWTManager(app)

@jwt_manager.token_in_blocklist_loader
def check_if_token_revoked(jwt_token, jwt_payload):
    jti = jwt_payload.get('jti')
    token = db.session.query(AccessTokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id)

db.init_app(app)
migrate = Migrate(compare_type=True)
migrate.init_app(app, db)


# register custom CLI commands
app.register_blueprint(custom_cli_commands)

# /admin
app.register_blueprint(admin_endpoints, url_prefix='/admin')

# /payment-settings
app.register_blueprint(stripe_settings_endpoints, url_prefix='/payment-settings')
app.register_blueprint(paypal_settings_endpoints, url_prefix='/payment-settings')

# /contacts
app.register_blueprint(contacts_tab_endpoints, url_prefix='/contacts/users')
app.register_blueprint(households_tab_endpoints, url_prefix='/contacts/households')
app.register_blueprint(contact_tags_tab_endpoints, url_prefix='/contacts/tags')
app.register_blueprint(contact_companies_endpoints, url_prefix='/contacts/companies')
app.register_blueprint(contact_interactions_endpoints, url_prefix='/contacts/interactions')
app.register_blueprint(contacts_todos_endpoints, url_prefix='/contacts/todos')
app.register_blueprint(contacts_volunteer_activity_endpoints, url_prefix='/contacts/volunteer-activity')

# /campaigns
app.register_blueprint(campaign_tab_endpoints, url_prefix='/campaigns')

# /forms
app.register_blueprint(forms_tab_endpoints, url_prefix='/forms')

# /p2p
app.register_blueprint(p2p_endpoints, url_prefix='/p2p')

# /donations
app.register_blueprint(pledges_tab_endpoints, url_prefix='/donations/pledges')
app.register_blueprint(one_time_transactions_tab_endpoints, url_prefix='/donations/one-time-transactions')
app.register_blueprint(donation_sources_endpoints, url_prefix='/donations/sources')
app.register_blueprint(recurring_transactions_tab_endpoints, url_prefix='/donations/recurring-transactions')
app.register_blueprint(donation_kpis_tab_endpoints, url_prefix='/donations/kpi')
app.register_blueprint(donation_summary_tab_endpoints, url_prefix='/donations/summary')

# /elements
app.register_blueprint(elements_tab_endpoints, url_prefix='/elements')

# /mailblasts
app.register_blueprint(mailblast_tab_endpoints, url_prefix='/mailblasts')

# /event
app.register_blueprint(packageviews, url_prefix='/package')
app.register_blueprint(promocode, url_prefix='/promocode')
app.register_blueprint(fieldviews, url_prefix='/field')
app.register_blueprint(eventviews, url_prefix='/event')
app.register_blueprint(eventbrite, url_prefix='/eventbrite')

# /keyword 
app.register_blueprint(keyword_endpoints, url_prefix='/keyword')

# /impact-area 
app.register_blueprint(impact_area_endpoints, url_prefix='/impact-area')

# /installment
app.register_blueprint(installments_endpoints, url_prefix='/installment')

# /report
app.register_blueprint(reports_tab_endpoints, url_prefix='/report')

@app.route('/')
def index():
    return '<h1>Hi</h1>'

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=os.getenv('PORT')
    )