from datetime import datetime, timedelta
from operator import and_

from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction


class TransactionSegments:
    def __init__(
        self, 
        days: int = 365,
        organization_id: str = None
    ):
        if not organization_id:
            raise Exception('`organization_id` is required in TransactionSegments()')

        self.organization_id = organization_id
        self.timespan = datetime.now() - timedelta(days=days)

        one_time_donations = self.one_time_donations()
        one_time_revenue = self.one_time_revenue()
        recurring_donations = self.recurring_donations()
        recurring_revenue = self.recurring_revenue()

        self.result = dict(
            one_time_donations = { 'number': len(one_time_donations), 'total_amount': sum([transaction.amount for transaction in one_time_donations]) },
            recurring_donations = { 'number': len(recurring_donations), 'total_amount': sum([transaction.amount for transaction in recurring_donations]) },
            one_time_revenue = { 'number': len(one_time_revenue), 'total_amount': sum([transaction.amount for transaction in one_time_revenue]) },
            recurring_revenue = { 'number': len(recurring_revenue), 'total_amount': sum([transaction.amount for transaction in recurring_revenue]) },
        )


    def one_time_donations(self):
        return OneTimeTransaction.query\
            .filter(
                and_(
                    OneTimeTransaction.created_at >= self.timespan,
                    and_(
                        OneTimeTransaction.organization_id == self.organization_id,
                        OneTimeTransaction.is_revenue == False
                    )
                )
            )\
            .all()
    
    
    def one_time_revenue(self):
        return OneTimeTransaction.query\
            .filter(
                and_(
                    OneTimeTransaction.created_at >= self.timespan,
                    and_(
                        OneTimeTransaction.organization_id == self.organization_id,
                        OneTimeTransaction.is_revenue == True
                    )
                )
            )\
            .all()
    
    
    def recurring_donations(self):
        return RecurringTransaction.query\
            .filter(
                and_(
                    RecurringTransaction.created_at >= self.timespan,
                    and_(
                        RecurringTransaction.organization_id == self.organization_id,
                        RecurringTransaction.is_revenue == False
                    )
                )
            )\
            .all()
    
    
    def recurring_revenue(self):
        return RecurringTransaction.query\
            .filter(
                and_(
                    RecurringTransaction.created_at >= self.timespan,
                    and_(
                        RecurringTransaction.organization_id == self.organization_id,
                        RecurringTransaction.is_revenue == True
                    )
                )
            )\
            .all()