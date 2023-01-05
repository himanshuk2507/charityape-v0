from flask import jsonify
from flask_jwt_extended import get_jwt

from skraggle.contact.Fundraising.models import Transactions
from flask_classy import FlaskView, route
from sqlalchemy import func, or_, and_
from skraggle.config import db
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg


class DonationCalculationsView(FlaskView):
    @user_required()
    def donations(self):
        data = [
            "total_donation_amount",
            "number_of_donations",
            "number_of_single_donations",
            "donations_from_pledges",
            "amount_of_single_donations",
            "average_donation_amount",
            "amount_of_recurring_donations",
            "number_of_recurring_donations",
            "contacts_represented",
            "amount_of_donations_from_pledges",
        ]
        calculations = {}
        # Calculation total donation amount
        total_donation_amount = (
            db.session.query(func.sum(Transactions.totalAmount))
            .filter(Transactions.organization_id == getOrg(get_jwt()))
            .where(Transactions.transaction_for == "donation",)
            .filter(Transactions.status == "accepted")
            .scalar()
        )
        # calculating number of donors
        number_of_donations = (
            Transactions.query.filter(Transactions.organization_id == getOrg(get_jwt()))
            .where(Transactions.transaction_for == "donation",)
            .filter(Transactions.status == "accepted")
            .count()
        )
        average_donation_amount = (
            db.session.query(func.avg(Transactions.totalAmount))
            .filter(Transactions.organization_id == getOrg(get_jwt()))
            .where(Transactions.transaction_for == "donation")
            .filter(Transactions.status == "accepted")
            .scalar()
        )
        number_of_contacts_represented = (
            Transactions.query.filter(Transactions.organization_id == getOrg(get_jwt()))
            .where(
                and_(
                    Transactions.transaction_from == "from_contact",
                    Transactions.transaction_for == "donation",
                )
            )
            .filter(Transactions.status == "accepted")
            .count()
        )

        donations_from_pledges = (
            Transactions.query.filter(Transactions.organization_id == getOrg(get_jwt()))
            .where(
                and_(
                    Transactions.transaction_for == "donation",
                    Transactions.transaction_from == "from_pledge",
                )
            )
            .filter(Transactions.status == "accepted")
            .count()
        )

        amount_from_pledges = (
            db.session.query(func.sum(Transactions.totalAmount))
            .filter(Transactions.organization_id == getOrg(get_jwt()))
            .where(
                and_(
                    Transactions.transaction_for == "donation",
                    Transactions.transaction_from == "from_pledge",
                )
            )
            .filter(Transactions.status == "accepted")
            .scalar()
        )

        calculations[data[0]] = total_donation_amount
        calculations[data[1]] = number_of_donations
        calculations[data[3]] = donations_from_pledges
        calculations[data[8]] = number_of_contacts_represented
        calculations[data[9]] = amount_from_pledges
        calculations[data[5]] = average_donation_amount

        return jsonify(calculations), 200


class TransactionCalculationsView(FlaskView):
    @user_required()
    def transactions(self):
        data = [
            "total_transaction_amount",
            "number_of_transactions",
            "number_of_transactions_accepted",
            "number_of_transactions_declined",
            "transactions_by_contacts",
            "transactions_by_donors",
            "average_transaction_amount",
        ]
        calculations = {}
        # Calculation total donation amount
        total_transaction_amount = (
            db.session.query(func.sum(Transactions.totalAmount))
            .filter(Transactions.organization_id == getOrg(get_jwt()))
            .filter(Transactions.status == "accepted")
            .scalar()
        )
        # calculating number of donors
        number_of_transactions = (
            db.session.query(Transactions)
            .filter(Transactions.organization_id == getOrg(get_jwt()))
            .count()
        )

        average_transaction_amount = (
            db.session.query(func.avg(Transactions.totalAmount))
            .filter(Transactions.organization_id == getOrg(get_jwt()))
            .where(Transactions.transaction_for == "donation")
            .filter(Transactions.status == "accepted")
            .scalar()
        )
        number_of_transactions_accepted = (
            Transactions.query.filter(Transactions.organization_id == getOrg(get_jwt()))
            .filter(Transactions.status == "accepted")
            .count()
        )

        number_of_transactions_declined = (
            Transactions.query.filter(Transactions.organization_id == getOrg(get_jwt()))
            .filter(Transactions.status == "declined")
            .count()
        )

        transactions_by_contacts = (
            Transactions.query.filter(Transactions.organization_id == getOrg(get_jwt()))
            .where(Transactions.transaction_from == "from_contact")
            .filter(Transactions.status == "accepted")
            .count()
        )

        transactions_by_donors = (
            Transactions.query.filter(Transactions.organization_id == getOrg(get_jwt()))
            .where(Transactions.transaction_from == "from_donor")
            .filter(Transactions.status == "accepted")
            .count()
        )
        calculations[data[0]] = total_transaction_amount
        calculations[data[1]] = number_of_transactions
        calculations[data[2]] = number_of_transactions_accepted
        calculations[data[3]] = number_of_transactions_declined
        calculations[data[4]] = transactions_by_contacts
        calculations[data[5]] = transactions_by_donors
        calculations[data[6]] = average_transaction_amount

        return jsonify(calculations), 200
