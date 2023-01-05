from datetime import datetime, timedelta
from typing import List
import numpy as np

import pandas as pd
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction


class DonorKPIs:
    def __init__(
        self,
        contact_users: List[ContactUsers] = [],
        contact_companies: List[ContactCompanies] = [],
        one_time_transactions: List[OneTimeTransaction] = [],
        recurring_transactions: List[RecurringTransaction] = [],
        schema: List[dict[str, str]] = []
    ) -> None:
        self.contact_users = contact_users
        self.contact_companies = contact_companies
        self.one_time_transactions = one_time_transactions
        self.recurring_transactions = recurring_transactions
        self.total_contacts = contact_users + contact_companies
        self.total_contacts_count = len(self.total_contacts)
        self.unique_donors, self.unique_donor_dates = self.calculate_unique_donors()
        self.schema = schema

    
    def contact_list_size(self):
        '''
        Number of contacts (users & companies).
        :returns int
        '''
        return len(self.contact_users) + len(self.contact_companies)

    
    def contact_list_growth_rate(self):
        '''
        Rate (in %) of growth in contacts size over the last 30 days.
        :returns str, with format 'f%'
        '''
        if self.total_contacts_count == 0:
            return '0.00%'

        delta = timedelta(days=30)
        now = datetime.now()
        a_month_ago = now - delta
        
        contacts_this_month = [contact for contact in (self.total_contacts) if contact.created_at >= a_month_ago]

        return '{:.2f}%'.format((len(contacts_this_month)/self.total_contacts_count) * 100)


    def contacts_acquired_each_month(self):
        '''
        Returns a dictionary dict[str, int] of dates (key) and the number of contacts acquired in each month (value).
        '''
        dates = [contact.created_at for contact in self.total_contacts]
        if len(dates) == 0:
            return {}

        dates.sort()
    
        minimum_date = dates[0]
        maximum_date = dates[-1] + timedelta(days=31) # add 31 days to the maximum to allow for Pandas slicing off the last date in the NumPy series
        
        date_range = pd.date_range(start=minimum_date, end=maximum_date, freq='1M').to_list()

        result = {}
        for i in range(len(date_range)):
            if i == 0:
                result[date_range[i].strftime('%m-%Y')] = len([contact.sn for contact in self.total_contacts if contact.created_at <= date_range[i]])
            else:
                result[date_range[i].strftime('%m-%Y')] = len([contact.sn for contact in self.total_contacts if contact.created_at <= date_range[i] and contact.created_at > date_range[i - 1]])
        return result

    
    def donor_list_size(self):
        '''
        Number of unique donors.
        :returns int
        '''
        return len(self.unique_donors)

    
    def donor_acquisition_rate_monthly(self):
        '''
        Number of new donors acquired monthly.
        :returns dict[str, int]
        '''
        dates = sorted(self.unique_donor_dates)
        if len(dates) == 0:
            return {}

        minimum_date = dates[0]
        maximum_date = dates[-1] + timedelta(days=31)
        
        date_range = pd.date_range(start=minimum_date, end=maximum_date, freq='1M').to_list()

        result = {}
        for i in range(len(date_range)):
            if i == 0:
                result[date_range[i].strftime('%m-%Y')] = len([donation_date for donation_date in dates if donation_date <= date_range[i]])
            else:
                result[date_range[i].strftime('%m-%Y')] = len([donation_date for donation_date in dates if donation_date <= date_range[i] and donation_date > date_range[i - 1]])

        return result

    
    def recurring_donor_acquisition_rate_monthly(self):
        dates = sorted([donation.created_at for donation in self.recurring_transactions])
        if len(dates) == 0:
            return {}

        minimum_date = dates[0]
        maximum_date = dates[-1] + timedelta(days=31)
        
        date_range = pd.date_range(start=minimum_date, end=maximum_date, freq='1M').to_list()

        result = {}
        for i in range(len(date_range)):
            if i == 0:
                result[date_range[i].strftime('%m-%Y')] = len([donation_date for donation_date in dates if donation_date <= date_range[i]])
            else:
                result[date_range[i].strftime('%m-%Y')] = len([donation_date for donation_date in dates if donation_date <= date_range[i] and donation_date > date_range[i - 1]])

        return result


    def new_donors_acquired_in_last_month(self):
        '''
        Percentage of recurring donors acquired in the last month.
        :returns str, with format 'f%'
        '''
        monthly_acquisition = self.donor_acquisition_rate_monthly()
        keys = list(monthly_acquisition.keys())
        if len(keys) == 0:
            return 0
        return monthly_acquisition[keys[-1]]

    
    def second_gift_conversion_rate(self):
        '''
        Percentage of donors who have donated at least twice.
        :returns str, with format 'f%'
        '''
        if len(self.unique_donors) == 0:
            return '0.00%'

        donors = []

        for donation in self.one_time_transactions + self.recurring_transactions:
            contact = donation.contact_id or donation.company_id
            donors.append(contact)

        returning_donors = []
        for contact in donors:
            if contact not in returning_donors:
                count = donors.count(contact)
                if count > 1:
                    returning_donors.append(contact)

        return '{:.2f}%'.format((len(returning_donors)/len(self.unique_donors)) * 100)


    def recurring_donor_lifetime_value(self):
        '''
        Average lifetime value of a recurrin donor.
        '''
        donations = {}

        for donation in self.one_time_transactions + self.recurring_transactions:
            contact = donation.contact_id or donation.company_id
            if contact in donations:
                donations[contact] += donation.amount
            else:
                donations[contact] = donation.amount

        amounts = list(donations.values())
        if len(amounts) == 0:
            return 0
        
        return np.median(amounts)


    def donor_retention_rate(self):
        '''
        Percentage of donors who have given over more than a year.
        '''
        donations = {}

        for donation in self.one_time_transactions + self.recurring_transactions:
            contact = donation.contact_id or donation.company_id
            if contact in donations:
                donations[contact].append(donation.created_at)
            else:
                donations[contact] = [donation.created_at]

        retained_donors_count = 0
        for dates in donations.values():
            minimum_date = min(dates)
            maximum_date = max(dates)
            if maximum_date - timedelta(days=365) > minimum_date:
                retained_donors_count += 1
        
        donations = len(donations.keys())
        if donations == 0:
            return '0.00%'
        return '{:.2f}%'.format((retained_donors_count/donations) * 100)

    
    def donor_churn_rate(self):
        '''
        Percentage of donors who have not given in at least a year.
        '''
        unique_donors = len(self.unique_donors)
        if unique_donors == 0:
            return '100.00%'

        donations = {}
        for donation in self.one_time_transactions + self.recurring_transactions:
            contact = donation.contact_id or donation.company_id
            if contact in donations:
                donations[contact].append(donation.created_at)
            else:
                donations[contact] = [donation.created_at]
        now = datetime.now()
        a_year_ago = now - timedelta(days=365)
        churn = 0
        for dates in donations.values():
            maximum_date = max(dates)
            if maximum_date < a_year_ago:
                churn += 1
        return '{}%'.format((churn/unique_donors) * 100)


    def recurring_donor_retention_rate(self):
        recurring_dates = [transaction.created_at for transaction in self.recurring_transactions]
        if len(recurring_dates) == 0:
            return '0.00%'

        minimum_date = min(recurring_dates)
        maximum_date = max(recurring_dates) + timedelta(days=31)
        months_in_interval = len(pd.date_range(start=minimum_date, end=maximum_date, freq='1M').to_list())
        if months_in_interval == 0:
            return '0.00%'
        
        unique_donors = {}
        for transaction in self.recurring_transactions:
            contact = transaction.contact_id or transaction.company_id
            if contact not in unique_donors:
                unique_donors[contact] = 0
            else:
                unique_donors[contact] += 1
        return '{:.2f}%'.format((len(unique_donors)/months_in_interval) * 100)



    def result(self):
        result = []

        for element in self.schema:
            value = None

            match element:
                case 'contact_list_size':
                    value = self.contact_list_size()
                case 'contact_list_growth_rate':
                    value = self.contact_list_growth_rate()
                case 'contacts_acquired_monthly':
                    value = self.contacts_acquired_each_month()
                case 'donor_list_size':
                    value = self.donor_list_size()
                case 'donor_acquisition_rate_monthly':
                    value = self.donor_acquisition_rate_monthly()
                case 'recurring_donor_acquisition_rate_monthly':
                    value = self.recurring_donor_acquisition_rate_monthly()
                case 'new_donors_acquired_in_last_month':
                    value = self.new_donors_acquired_in_last_month()
                case 'second_gift_conversion_rate':
                    value = self.second_gift_conversion_rate()
                case 'recurring_donor_lifetime_value':
                    value = self.recurring_donor_lifetime_value()
                case 'donor_retention_rate':
                    value = self.donor_retention_rate()
                case 'donor_churn_rate':
                    value = self.donor_churn_rate()
                case 'recurring_donor_retention_rate':
                    value = self.recurring_donor_retention_rate()
            result.append(
                dict(name=element, value=value)
            )
        
        return result


    def calculate_unique_donors(self):
        donors = []
        donor_dates = []

        for donation in self.one_time_transactions + self.recurring_transactions:
            contact = donation.contact_id or donation.company_id
            if contact not in donors:
                donors.append(contact)
                donor_dates.append(donation.created_at)

        return donors, donor_dates


donor_kpis_schema = [
    { "name": "contact_list_size", "label": "Contact List Size (Individuals + Companies)", "description": "Total number of contacts (current and potential donors)." },
    { "name": "contact_list_growth_rate", "label": "Contact List Growth Rate", "description": "The rate at which your contact list is growing monthly." },
    { "name": "contacts_acquired_monthly", "label": "Contacts Acquired (Monthly)", "description": "Number of new contacts added each month." },
    { "name": "donor_list_size", "label": "Donor List Size", "description": "The number of contacts in your database who have donated." },
    { "name": "donor_acquisition_rate_monthly", "label": "Donor Acquisition Rate (Monthly)", "description": "The rate at which your donor list is growing monthly." },
    { "name": "recurring_donor_acquisition_rate_monthly", "label": "Recurring Donor Acquisition Rate (Monthly)", "description": "Percentage of recurring donors acquired month-to-month." },
    { "name": "new_donors_acquired_in_last_month", "label": "New Donors Acquired (Monthly)", "description": "Number of new donors acquired in the last month." },
    { "name": "second_gift_conversion_rate", "label": "Second Gift Conversion Rate", "description": "Fraction of donors in your database who have given at least twice." },
    { "name": "recurring_donor_lifetime_value", "label": "Recurring Donor Lifetime Value", "description": "Average amount a recurring donor is likely to contribute over their philanthropic lifespan." },
    { "name": "donor_retention_rate", "label": "Donor Retention Rate", "description": "The percentage of donors who give to your organisation one year and then give again the following year." },
    { "name": "donor_churn_rate", "label": "Donor Churn Rate", "description": "The percentage of donors who have not given to your organisation for more than a year." },
    { "name": "recurring_donor_retention_rate", "label": "Recurring Donor Retention Rate", "description": "Percentage of recurring donors retained month-to-month." },
]