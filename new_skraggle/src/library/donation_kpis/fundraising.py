from math import floor
from typing import List
import numpy as np

from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction


class FundraisingKPIs:
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
        self.one_time_donation_amounts, self.recurring_donation_amounts, self.donation_amounts = self.list_donation_amounts()
        self.schema = schema

    
    def median_gift_size(self):
        if len(self.donation_amounts) == 0:
            return 0
        return np.median(self.donation_amounts)

    
    def recurring_donor_median_gift_size(self):
        if len(self.recurring_donation_amounts) == 0:
            return 0
        return np.median(self.recurring_donation_amounts)


    def average_gift_size(self):
        if len(self.donation_amounts) == 0:
            return 0
        return np.mean(self.donation_amounts)

    
    def recurring_donor_average_gift_size(self):
        if len(self.recurring_donation_amounts) == 0:
            return 0
        return np.mean(self.recurring_donation_amounts)

    
    def fraction_of_gifts_from_campaigns(self):
        amounts = len(self.donation_amounts)
        if amounts == 0:
            return '0.00%'

        campaign_gifts = [donation for donation in self.one_time_transactions + self.recurring_transactions if donation.campaign_id != None]
        return '{:.2f}%'.format((len(campaign_gifts)/amounts) * 100)


    def fraction_from_small_gifts(self):
        if len(self.donation_amounts) == 0:
            return '0.00%'
        amounts = sorted(self.donation_amounts)
        total = len(amounts)
        small_gifts = amounts[0:floor(total/4)]
        return '{:.2f}%'.format((len(small_gifts)/total) * 100)
    
    
    def fraction_from_major_gifts(self):
        if len(self.donation_amounts) == 0:
            return '0.00%'
        amounts = sorted(self.donation_amounts)
        total = len(amounts)
        major_gifts = amounts[floor(total * 3/4):]
        return '{:.2f}%'.format((len(major_gifts)/total) * 100)
    
    
    def percentage_of_gifts_from_online(self):
        total_donations = len(self.donation_amounts)
        if total_donations == 0:
            return '0.00%'
        online_gifts = [donation.sn for donation in self.one_time_transactions + self.recurring_transactions if donation.payment_method.startswith('online')]
        return '{:.2f}'.format((len(online_gifts)/total_donations) * 100)

    
    def recurring_donations_as_a_percentage_of_total_funds_raised(self):
        if len(self.donation_amounts) == 0:
            return '0.00%'
        return '{:.2f}%'.format((sum(self.recurring_donation_amounts)/sum(self.donation_amounts)) * 100)

    
    def recurring_donors_as_a_percentage_of_total_donors(self):
        if len(self.donation_amounts) == 0:
            return '0.00%'
        recurring_donors = set([donation.contact_id or donation.company_id for donation in self.recurring_transactions])
        return '{:.2f}%'.format((len(recurring_donors)/len(self.donation_amounts)) * 100)


    def result(self):
        result = []

        for element in self.schema:
            value = None

            match element:
                case 'median_gift_size':
                    value = self.median_gift_size()
                case 'recurring_donor_median_gift_size':
                    value = self.recurring_donor_median_gift_size()
                case 'average_gift_size':
                    value = self.average_gift_size()
                case 'recurring_donor_average_gift_size':
                    value = self.recurring_donor_average_gift_size()
                case 'fraction_of_gifts_from_campaigns':
                    value = self.fraction_of_gifts_from_campaigns()
                case 'fraction_from_small_gifts':
                    value = self.fraction_from_small_gifts()
                case 'fraction_from_major_gifts':
                    value = self.fraction_from_major_gifts()
                case 'percentage_of_gifts_from_online':
                    value = self.percentage_of_gifts_from_online()
                case 'recurring_donations_as_a_percentage_of_total_funds_raised':
                    value = self.recurring_donations_as_a_percentage_of_total_funds_raised()
                case 'recurring_donors_as_a_percentage_of_total_donors':
                    value = self.recurring_donors_as_a_percentage_of_total_donors()

            result.append(
                dict(name=element, value=value)
            )
        
        return result


    def list_donation_amounts(self):
        one_time = [transaction.amount for transaction in self.one_time_transactions]
        recurring = [transaction.amount for transaction in self.recurring_transactions]

        return one_time, recurring, one_time + recurring


fundraising_kpis_schema = [
    { "name": "median_gift_size", "label": "Median Gift Size", "description": "Your average gift size can often be skewed by a few small or large donations. Looking instead at your median gift size gives a better indication of the \"middle\" of your data. This KPI tells you the typical gift size your organization received. The median is computed by organizing all gifts in order from smallest to largest, then selecting the middle value in the data set." },
    { "name": "recurring_donor_median_gift_size", "label": "Recurring Donor Median Gift Size", "description": "Median of recurring gifts." },
    { "name": "average_gift_size", "label": "Average Gift Size", "description": "The average size of a gift (donation) from your donors." },
    { "name": "recurring_donor_average_gift_size", "label": "Recurring Donor Average Gift Size", "description": "Mean of recurring gifts." },
    { "name": "fraction_of_gifts_from_campaigns", "label": "Fraction of Gifts from Campaigns", "description": "Percentage of total gifts that were made to a campaign." },
    { "name": "fraction_from_small_gifts", "label": "Fraction of Donations from Small Gifts", "description": "Small gifts are important as they have the chance to grow with effective stewardship, or drop off all together as donors lapse. Make sure you are aware of how many \"small gifts\" you have as a percentage of the whole to always balance these with other categories and ensure you are nurturing them into other categories over time." },
    { "name": "fraction_from_major_gifts", "label": "Fraction of Donations from Major Gifts", "description": "Just like it's important to understand how many donors are in the smallest 25%, you need to know how many major donors you are stewarding. This number should grow over time if you are doing well at stewarding donors and developing their commitment to your cause and trust in your organization." },
    { "name": "percentage_of_gifts_from_online", "label": "Percentage Of Gifts From Online (Year To Date)", "description": "Fraction of donations received from online donation forms calculated as a percentage of your total donations year to date. Note: This metric is only tracked for donations made in Skraggle." },
    { "name": "recurring_donations_as_a_percentage_of_total_funds_raised", "label": "Recurring Donations As A Percentage Of Total Funds Raised", "description": "Percentage of your total donations that come from recurring gifts." },
    { "name": "recurring_donors_as_a_percentage_of_total_donors", "label": "Recurring Donors As A Percentage Of Total Donors", "description": "Fraction of your donors who give recurring gifts." }
]