from skraggle.constants import DEFAULT_PAGE_SIZE, BASE_URL
from skraggle.config import db
from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.paginator_util import paginated_response
from flask import  abort


def paginator(page_number, table, order_id, common_url):
    total_records = db.session.query(table).count()
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    data = (
        table.query.order_by(getattr(table, order_id))
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    data = [dict_resp(contact) for contact in data]
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    return paginated_response(
        page_number, total_records, data, previous_page, next_page
    )


def paginate_memberships(page_number, table, contact_id, common_url):
    total_records = db.session.query(table).count()
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    data = (
        table.query.filter_by(contact_id=contact_id)
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    data = [dict_resp(contact) for contact in data]
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    return paginated_response(
        page_number, total_records, data, previous_page, next_page
    )


def paginator_search(page_number, table, common_url):
    total_records = table.count()
    page_number = int(page_number)
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    data = (
        table.offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    data = [dict_resp(datum) for datum in data]
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    return paginated_response(
        page_number, total_records, data, previous_page, next_page
    )
    

def get_paginated_list(results, url, start):
    start = int(start)
    limit = 10
    count = len(results)
    # if count < start or limit < 0:
    #     abort(404)
    # make response
    obj = {}
    obj['start'] = start
    # obj['limit'] = limit
    obj['count'] = count
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        # limit_copy = start - 1
        obj['previous'] = url + '/%d' % (start_copy)
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '/%d' % (start_copy)
    # finally extract result according to bounds
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    return obj