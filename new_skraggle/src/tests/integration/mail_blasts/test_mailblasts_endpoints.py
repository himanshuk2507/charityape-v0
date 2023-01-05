from flask import Response

from src.tests.integration.admin.fixtures import authorization_header
from src.tests.integration.mail_blasts.fixtures import MailBlastFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_fetch_mailblasts_route(test_client):
    """
    GIVEN a request to GET /mailblasts endpoint
    WHEN there exist mail blast entities
    THEN the route returns list of dicts of mail blasts
    """
    response: Response = test_client.get('/mailblasts', headers=authorization_header())
    assert_is_ok(response)


def test_create_mailblast_route(test_client):
    """
    GIVEN a request to POST /mailblasts endpoint
    WHEN the request body contains mail blast parameters
    THEN the route creates new mail blast entry
    """
    data = MailBlastFixture.default_obj()
    response: Response = test_client.post('/mailblasts', json=data, headers=authorization_header())
    assert_is_ok(response)


# def test_fetch_mailblast_subscriptions_route(test_client):
#     """
#     GIVEN a request to GET /mailblasts/subscription endpoint
#     THEN the route returns list of contacts subscribed to mailblasts
#     """
#     response: Response = test_client.get('/mailblasts/subscription', headers=authorization_header())
#     assert_is_ok(response)


def test_fetch_mailblast_by_id_route(test_client):
    """
    GIVEN a request to GET /mailblasts/<uuid> endpoint
    WHEN there exists a mailblast entity with the given uuid
    THEN the route returns dict of the corresponding uuid mailblast
    """
    mail_blast_id = MailBlastFixture().id
    response: Response = test_client.get(f'/mailblasts/{mail_blast_id}', headers=authorization_header())
    assert_is_ok(response)


def test_fetch_mailing_list_route(test_client):
    """
    GIVEN a request to GET /mailblasts/<uuid>/mailing-list endpoint
    WHEN there exists a mailblast entity with the given uuid
    THEN the route Retrieve mailing list for uuid mailblast
    """
    mail_blast_id = MailBlastFixture().id
    response: Response = test_client.get(f'/mailblasts/{mail_blast_id}/mailing-list', headers=authorization_header())
    assert_is_ok(response)


def test_update_mailblast_by_id_route(test_client):
    """
    GIVEN a request to PATCH /mailblasts/<uuid> endpoint
    WHEN there exists a mailblast entity with the given uuid
    THEN the route updates the passed field values for the mail blast entity corresponding to the uuid
    """
    mail_blast_id = MailBlastFixture().id
    data = {
        "name": "New Favourite Vegetables",
        "archived": False
    }
    response: Response = test_client.patch(f'/mailblasts/{mail_blast_id}', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_delete_mailblasts_by_id_route(test_client):
    """
    GIVEN a request to DELETE /mailblasts endpoint
    WHEN the request body contains list of mailblast ids to delete
    THEN the route deletes the corresponding mailblast entries
    """
    mail_blast_id = MailBlastFixture().id
    data = {"mailblasts": [mail_blast_id]}
    response: Response = test_client.delete('/mailblasts', json=data, headers=authorization_header())
    assert_is_ok(response)
