from math import floor
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse
from flask import Blueprint, request

from src.library.utility_classes.request_response import Response


installments_endpoints = Blueprint('installments_endpoints', __name__)


'''
@route GET /installments
@desc Calculate installmemts
@access Public
'''
@installments_endpoints.route('', methods=['GET'])
def calculate_installments_route():
    query_params = parse_qs(urlparse(request.url).query)
    
    def get(key: str = None):
        if key is None:
            return None
        query_key = query_params.get(key)
        if not query_key:
            return None
        return None if len(query_key) == 0 else query_key[0]

    total = get('total')
    interval = get('interval')
    payment = get('payment')

    if interval not in ['week', 'month', 'year']:
        return Response(False, '`interval` must be one of week, month, year').respond()
    try:
        total = float(total)
        payment = float(payment)
    except (TypeError, ValueError):
        return Response(False, '`total` and `payment` must be valid numbers').respond()

    delta = timedelta(weeks=1)
    if interval == 'month':
        delta = timedelta(weeks=4)
    elif interval == 'year':
        delta = timedelta(days=365)

    remainder = total % payment
    last_date = datetime.now()
    data = [dict(amount=payment, expected_at=last_date)]
    for _ in range(int(total/payment)-1):
        last_date = last_date + delta
        data.append(dict(amount=payment, expected_at=last_date))
    if remainder != 0:
        data.append(dict(amount=remainder, expected_at=last_date+delta))
            
    return Response(True, data).respond()