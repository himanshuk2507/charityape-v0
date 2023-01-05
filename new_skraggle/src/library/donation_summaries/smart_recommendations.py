from math import floor
from typing import List

from statistics import median

from src.app_config import TransactionMixin


def smart_ask(transactions: List[TransactionMixin] = [], contact = None):
    if transactions is None or contact is None:
        raise Exception('`transactions` and `contact` are required in smart_ask()')
    
    contact_amounts = []
    organization_amounts = []

    for transaction in transactions:
        transaction_contact = transaction.contact_id or transaction.company_id
        if transaction_contact == contact:
            contact_amounts.append(transaction.amount)
        organization_amounts.append(transaction.amount)

    target = median(contact_amounts) if len(contact_amounts) > 2 else median(organization_amounts) if len(organization_amounts) > 0 else 0
    unit = floor(target/3)
    
    return dict(
        minimum=unit*3,
        maximum=unit*4,
        recommended=target
    )


def time_of_year(transactions: List[TransactionMixin] = [], contact = None):
    if transactions is None or contact is None:
        raise Exception('`transactions` and `contact` are required in smart_ask()')

    contact_transactions = [transaction for transaction in transactions if transaction.contact_id == contact or transaction.company_id == contact]
    if len(contact_transactions) < 2:
        transactions = contact_transactions
    
    dates = []
    for transaction in transactions:
        dates.append(
            transaction.created_at.strftime('%Y-%m')
        )
    return median(dates) if len(dates) > 0 else None