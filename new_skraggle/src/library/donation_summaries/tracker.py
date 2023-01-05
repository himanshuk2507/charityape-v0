from datetime import datetime, timedelta
from operator import and_
from typing import List

import pandas as pd

from src.app_config import TransactionMixin

from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction


class DonationTracker:
    def __init__(
        self,
        days: int = 30,
        organization_id: str = None
    ):
        if not organization_id:
            raise Exception('`organization_id` is required in DonationTracker()')
            
        delta = datetime.now() - timedelta(days=days)
        one_time_transactions = OneTimeTransaction.query\
            .filter(
                and_(
                    OneTimeTransaction.created_at >= delta,
                    and_(
                        OneTimeTransaction.organization_id == organization_id,
                        OneTimeTransaction.is_revenue == False
                    )
                )
            )\
            .all()
        recurring_transactions = RecurringTransaction.query\
            .filter(
                and_(
                    RecurringTransaction.created_at >= delta,
                    and_(
                        RecurringTransaction.organization_id == organization_id,
                        RecurringTransaction.is_revenue == False
                    )
                )
            )\
            .all()
        self.result = TransactionTracker(
            days = days,
            transactions = one_time_transactions + recurring_transactions
        ).result()



class RevenueTracker:
    def __init__(
        self,
        days: int = 30,
        organization_id: str = None
    ):
        if not organization_id:
            raise Exception('`organization_id` is required in RevenueTracker()')
            
        delta = datetime.now() - timedelta(days=days)
        one_time_transactions = OneTimeTransaction.query\
            .filter(
                and_(
                    OneTimeTransaction.created_at >= delta,
                    and_(
                        OneTimeTransaction.organization_id == organization_id,
                        OneTimeTransaction.is_revenue == True
                    )
                )
            )\
            .all()
        recurring_transactions = RecurringTransaction.query\
            .filter(
                and_(
                    RecurringTransaction.created_at >= delta,
                    and_(
                        RecurringTransaction.organization_id == organization_id,
                        RecurringTransaction.is_revenue == True
                    )
                )
            )\
            .all()
        self.result = TransactionTracker(
            days = days,
            transactions = one_time_transactions + recurring_transactions
        ).result()



class TransactionTracker:
    def __init__(
        self, 
        days: int = 30,
        transactions: List[TransactionMixin] = [],
    ):
        self.timespan = datetime.now() - timedelta(days=days)
        self.transactions = transactions
        self.date_range = self.calculate_date_range()
        self.date_range_length = len(self.date_range)

    
    def result(self):
        result = {}
        for i in range(len(self.date_range)):
            max_date = self.string_to_date(str(self.date_range[i]))
        
            if i == self.date_range_length - 1:
                result[self.date_range[i].strftime('%m-%Y')] = sum([transaction.amount for transaction in self.transactions if transaction.created_at <= max_date])
            else:
                min_date = self.string_to_date(str(self.date_range[i + 1]))
                result[self.date_range[i].strftime('%m-%Y')] = sum([transaction.amount for transaction in self.transactions if transaction.created_at > min_date and transaction.created_at <= min_date])
        return result


    def string_to_date(self, date_str: str):
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')


    def calculate_date_range(self):
        return pd.date_range(
                start=self.timespan, 
                end=(
                    datetime.now() + timedelta(days=31)
                ), 
                freq='1M'
            ).to_list()



class TimeOfYearTracker:
    def __init__(
        self, 
        days: int = 30,
        organization_id: str = None
    ):
        if not organization_id:
            raise Exception('`organization_id` is required in TimeOfYearTracker()')
        self.timespan = datetime.now() - timedelta(days=days)
        self.date_range = self.calculate_date_range()
        self.date_range_length = len(self.date_range)
        self.transactions = OneTimeTransaction.query\
            .filter(
                and_(
                    OneTimeTransaction.organization_id == organization_id,
                    OneTimeTransaction.created_at >= self.timespan,
                )
            )\
            .all() + \
                RecurringTransaction.query\
            .filter(
                and_(
                    RecurringTransaction.organization_id == organization_id,
                    RecurringTransaction.created_at >= self.timespan,
                )
            )\
            .all()

    
    def result(self):
        result = {}
        for i in range(len(self.date_range)):
            max_date = self.string_to_date(str(self.date_range[i]))
        
            if i == self.date_range_length - 1:
                result[self.date_range[i].strftime('%m-%Y')] = len([transaction.amount for transaction in self.transactions if transaction.created_at <= max_date])
            else:
                min_date = self.string_to_date(str(self.date_range[i + 1]))
                result[self.date_range[i].strftime('%m-%Y')] = len([transaction.amount for transaction in self.transactions if transaction.created_at > min_date and transaction.created_at <= min_date])
        return result


    def string_to_date(self, date_str: str):
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')


    def calculate_date_range(self):
        return pd.date_range(
                start=self.timespan, 
                end=(
                    datetime.now() + timedelta(days=31)
                ), 
                freq='1M'
            ).to_list()