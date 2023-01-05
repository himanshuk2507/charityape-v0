from src.contacts.households.models import Households
from src.library.utility_classes.paginator import Paginator
from src.tests.integration.admin.fixtures import AdminFixture



def test_paginator_constructor():
    """
    Test that the Paginator works as expected and returns correct rows count
    """
    organization_id = AdminFixture().organization_id
    for i in range(10):
        data = {"name": f"Household {i}", "organization_id": organization_id}
        Households.register(data)
        

    cursor = -1
    households = Paginator(
        model=Households,
        query=Households.query,
        query_string=Paginator.get_query_string(f"127.0.0.1:5000/households?cursor={cursor}&limit=8&direction=after"),
        organization_id=organization_id
    ).result

    household_rows = len(households['rows'])
    assert household_rows == 8
    assert households['has_next'] is True
    assert households['has_previous'] is False

    cursor = households['rows'][household_rows - 1]['sn']

    households = Paginator(
        model=Households,
        query=Households.query,
        query_string=Paginator.get_query_string(f"127.0.0.1:5000/households?cursor={cursor}&limit=8&direction=after"),
        organization_id=organization_id
    ).result

    assert households['has_next'] is False
    assert households['has_previous'] is True
    assert len(households['rows']) == 4

    cursor = households['rows'][0]['sn']
    households = Paginator(
        model=Households,
        query=Households.query,
        query_string=Paginator.get_query_string(f"127.0.0.1:5000/households?cursor={cursor}&limit=8&direction=before"),
        organization_id=organization_id
    ).result

    assert households['has_next'] is True
    assert households['has_previous'] is False
    assert len(households['rows']) == 8