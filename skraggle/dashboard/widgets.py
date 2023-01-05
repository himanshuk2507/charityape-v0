from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.config import db
from skraggle.contact.models import ContactUsers
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg

widgetview = Blueprint("widgetview", __name__)


@widgetview.route("/raised/<int:id>")
@user_required()
def raised_report(id):
    donated = ContactUsers.query.filter_by(
        id=id, organization_id=getOrg(get_jwt())
    ).first()
    print(donated.Total_Donations)
    donated.Total_Donations = 5
    donated.Total_Transactions = 20
    db.session.commit()
    return f"{donated.Total_Donations}"


@widgetview.route("/donations/<int:id>")
@user_required()
def donations_widget(id):
    user = ContactUsers.query.filter_by(id=id, organization_id=getOrg(get_jwt())).first()
    goal_achieved = 0
    recent_transactions = ContactUsers.query.order_by(-ContactUsers.id).limit(10).all()
    transactions_made = user.Total_Transactions
    upcoming_transactions = 0
    payment_method = "NA"
    data = {
        "Payment Method": payment_method,
        "Recent Upcoming Transactions": upcoming_transactions,
        "Recent_Transactions": [x.Total_Transactions for x in recent_transactions],
        "Number of Transactions Made": transactions_made,
        "Donation Goal Achieved": goal_achieved,
    }
    return jsonify(data)
