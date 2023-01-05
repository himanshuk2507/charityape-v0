from datetime import datetime, timedelta
from typing import List

from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction


class FundraisingActivitySummary:
    def __init__(
        self, 
        days: int = 30,
        contact_users: List[ContactUsers] = [],
        contact_companies: List[ContactCompanies] = [],
        one_time_transactions: List[OneTimeTransaction] = [],
        recurring_transactions: List[RecurringTransaction] = [],
    ):
        self.contact_users = contact_users
        self.contact_companies = contact_companies
        self.one_time_transactions = one_time_transactions
        self.recurring_transactions = recurring_transactions
        self.total_contacts = contact_users + contact_companies
        self.total_contacts_count = len(self.total_contacts)

        self.timespan = datetime.now() - timedelta(days=days)

    
    def donations(self):
        return sum([donation.amount for donation in self.one_time_transactions + self.recurring_transactions if donation.is_revenue == False and donation.created_at >= self.timespan])
    
    
    def revenue(self):
        return sum([donation.amount for donation in self.one_time_transactions + self.recurring_transactions if donation.is_revenue == True and donation.created_at >= self.timespan])

    
    def contacts(self):
        return len([0 for contact in self.total_contacts if contact.created_at >= self.timespan])


    def result(self):
        return dict(
            donations = self.donations(),
            revenue = self.revenue(),
            contacts = self.contacts()
        )

