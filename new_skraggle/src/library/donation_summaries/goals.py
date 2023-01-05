from datetime import datetime, timedelta
from typing import List
from operator import and_

from src.app_config import TransactionMixin
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction


class DonationGoals:
    def __init__(
        self,
        organization_id: str = None,
        monthly_goal: int = None,
        quarterly_goal: int = None,
        yearly_goal: int = None,
    ):
        if not organization_id:
            raise Exception('`organization_id` is required in DonationGoals()')
            
        delta = datetime.now() - timedelta(days=365)
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
        self.result = TransactionGoals(
            transactions = one_time_transactions + recurring_transactions,
            monthly_goal = monthly_goal,
            quarterly_goal = quarterly_goal,
            yearly_goal = yearly_goal,
        ).process()



class RevenueGoals:
    def __init__(
        self,
        organization_id: str = None,
        monthly_goal: int = None,
        quarterly_goal: int = None,
        yearly_goal: int = None,
    ):
        if not organization_id:
            raise Exception('`organization_id` is required in RevenueGoals()')
            
        delta = datetime.now() - timedelta(days=365)
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
        self.result = TransactionGoals(
            transactions = one_time_transactions + recurring_transactions,
            monthly_goal = monthly_goal,
            quarterly_goal = quarterly_goal,
            yearly_goal = yearly_goal,
        ).process()



class TransactionGoals:
    def __init__(
        self,
        monthly_goal: int = None,
        quarterly_goal: int = None,
        yearly_goal: int = None,
        transactions: List[TransactionMixin] = []
    ):
        self.monthly_goal = monthly_goal
        self.quarterly_goal = quarterly_goal
        self.yearly_goal = yearly_goal
        self.transactions = transactions


    def process(self):
        now = datetime.now()

        deltas = [
            dict(delta = timedelta(days=31), raised = 0, goal = self.monthly_goal, type = 'monthly'),
            dict(delta = timedelta(days=93), raised = 0, goal = self.quarterly_goal, type = 'quarterly'),
            dict(delta = timedelta(days=365), raised = 0, goal = self.yearly_goal, type = 'yearly')
        ]

        for transaction in self.transactions:
            for delta in deltas:
                if transaction.created_at >= now - delta['delta']:
                    delta['raised'] += transaction.amount

        for delta in deltas:
            delta.pop('delta')
        return deltas
        