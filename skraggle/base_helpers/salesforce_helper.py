import requests
from urllib.parse import quote, urlencode

from flask_jwt_extended import get_jwt
from simple_salesforce import Salesforce, SalesforceExpiredSession

from skraggle.base_helpers.crypter import Crypt
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.base_helpers.object_utility import ObjectHandler
from skraggle.config import db
from skraggle.contact.models import ContactUsers
from skraggle.integrations.models import SalesforceDetails


class SalesforceOAuth2:
    """
        Salesforce Web Server Oauth Authentication Flow
    """

    _authorization_url = "/services/oauth2/authorize"
    _token_url = "/services/oauth2/token"

    def __init__(self, client_id, client_secret, redirect_uri, sandbox):
        """
        Create SalesforceOauth2 object
        :param client_id: Connected App's Consumer Key
        :param client_secret: Connected App's Consumer Secret
        :param redirect_uri: Callback URL once logged in
        :param sandbox: Boolean flag to determine authentication site
        """
        if sandbox:
            self.auth_site = "https://test.salesforce.com"
        else:
            self.auth_site = "https://login.salesforce.com"
        self.redirect_uri = redirect_uri
        self._client_id = client_id
        self._client_secret = client_secret

    def authorize_login_url(self, state):
        """
        URL to login through Salesforce
        :return: Redirect URL for Oauth2 authentication
        """
        url = "{0}{1}?".format(self.auth_site, self._authorization_url)
        args = {
            "response_type":'code',
            "client_id": self._client_id,
            "redirect_uri": self.redirect_uri,
            "state": str(state),
        }
        return url + urlencode(args)

    def get_access_token(self, code):
        """
        Sets the body of the POST request
        """
        body = {
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": code,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        response = self._request_token(body)
        return response

    def get_new_access_token(self, refresh_token):
        """
        Sets the body of the POST request
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic",
        }
        body = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        response = self._request_token(body)

        return response.json()

    def _request_token(self, data):
        """
        Sends a POST request to Salesforce to authenticate credentials
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(
            "{site}{token_url}".format(site=self.auth_site, token_url=self._token_url),
            data=data,
            headers=headers,
        )

        return response

    def get_user_info(self, access_token, instance_url):
        headers = {
            "Content-Type": "application/json",
            "Acccept_Encoding": "gzip",
            "Authorization": "Bearer " + access_token,
        }
        response = requests.post(f"{instance_url}", headers=headers)
        return response


class SalesforceConnect:
    _authorization_url = "/services/oauth2/authorize"
    _token_url = "/services/oauth2/token"

    def __init__(self, oauth, logged_user):
        self.oauth = oauth
        self.logged_user = logged_user

    def get_fields(self, access_token, query_url):
        headers = {
            "Content-Type": "application/json",
            "Acccept_Encoding": "gzip",
            "Authorization": "Bearer " + access_token,
        }
        response = requests.get(f"{query_url}", headers=headers)
        return response

    def get_connection(self):
        if self.logged_user.salesforce_connected:
            hider = Crypt()
            salesforce_id = self.logged_user.salesforce_id
            connection = SalesforceDetails.query.filter_by(
                organization_id=getOrg(get_jwt()), salesforce_id=salesforce_id
            ).first()
            access_token = hider.decrypt(connection.access_token)
            instance_url = connection.instance_url
            # Check If access token is expired by making a dump request with our access token."
            try:
                sf = Salesforce(instance_url=instance_url, session_id=access_token)
                query = "SELECT Name,MailingAddress,Email,Phone,Birthdate, Account.Id FROM Contact"
                data = sf.query_all(query)
                return {"access_token": access_token, "instance_url": instance_url}
            # "If Access Token is expired ,refresh and generates a New Access Token "

            except SalesforceExpiredSession:
                refresh_token = hider.decrypt(connection.refresh_token)
                fresh_accesstoken = self.oauth.get_new_access_token(refresh_token)[
                    "access_token"
                ]
                connection.access_token = hider.encrypt(fresh_accesstoken)
                db.session.commit()
                access_token = hider.decrypt(connection.access_token)
                instance_url = connection.instance_url
                return {"access_token": access_token, "instance_url": instance_url}


class SalesforceMapper:
    def get_fields_map(self, mappings, table_to_map):
        salesforce_fields_map = [
            {
                rule["rule"]["salesforce_object_name"]: rule["rule"][
                    "salesforce_field_name"
                ]
            }
            for rule in mappings
            if rule["rule"]["skraggle_object_name"] == table_to_map
        ]
        skraggle_fields_map = [
            {rule["rule"]["skraggle_object_name"]: rule["rule"]["skraggle_field_name"]}
            for rule in mappings
            if rule["rule"]["skraggle_object_name"] == table_to_map
        ]
        data_map = {
            "skraggle": skraggle_fields_map,
            "salesforce": salesforce_fields_map,
        }
        return data_map

    def sync(self, mappings, organization_id, connection, sync_type):
        records_synced, tables_synced, tables_skipped = 0, [], []
        salesforce_objects_synced = []
        skraggle_tables_to_sync = list(
            set(x["rule"]["skraggle_object_name"] for x in mappings)
        )
        for _table_to_sync in skraggle_tables_to_sync:
            skraggle_fields_to_map = list(
                x["rule"]["skraggle_field_name"]
                for x in mappings
                if x["rule"]["skraggle_object_name"] == _table_to_sync
            )
            salesforce_fields_to_map = list(
                x["rule"]["salesforce_field_name"]
                for x in mappings
                if x["rule"]["skraggle_object_name"] == _table_to_sync
            )
            salesforce_fields_map = self.get_fields_map(mappings, _table_to_sync)[
                "salesforce"
            ]
            skraggle_fields_map = self.get_fields_map(mappings, _table_to_sync)[
                "skraggle"
            ]
            fields_to_fetch = {
                k: v for (k, v) in zip(skraggle_fields_to_map, salesforce_fields_map)
            }
            fields_to_dump = {
                k: v for (k, v) in zip(salesforce_fields_to_map, skraggle_fields_map)
            }
            _table_to_dump = list(
                set(
                    x["rule"]["salesforce_object_name"]
                    for x in mappings
                    if x["rule"]["skraggle_object_name"] == _table_to_sync
                )
            )
            sync = ObjectHandler(
                _table_to_sync, organization_id, sobject=_table_to_dump[0]
            )
            records = sync.process(
                connection,
                fields_to_fetch,
                skraggle_fields_to_map,
                salesforce_fields_to_map,
                fields_to_dump,
                sync_type,
            )
            if not records["success"]:
                tables_skipped.append(str(_table_to_sync))
                continue
            success = None
            if sync_type == "import":
                success = sync.import_records(records["message"])
            elif sync_type == "export":
                success = sync.export_records(records["message"], connection)
            if not success["success"]:
                tables_skipped.append(str(_table_to_sync))
                continue
            records_synced += records["records_synced"]
            tables_synced.append(
                {
                    "table_synced": _table_to_sync,
                    "fields_synced": skraggle_fields_to_map,
                }
            )
            sf_obj = list(
                x["rule"]["salesforce_object_name"]
                for x in mappings
                if x["rule"]["skraggle_object_name"] == _table_to_sync
            )
            sf_fields = list(
                x["rule"]["salesforce_field_name"]
                for x in mappings
                if x["rule"]["skraggle_object_name"] == _table_to_sync
            )
            salesforce_synced_details = {
                "salesforce_objects_synced": sf_obj[0],
                "salesforce_fields_synced": sf_fields,
            }
            salesforce_objects_synced.append(salesforce_synced_details)

        resp = {
            "message": "Sync Successfull",
            "success": True,
            "sync_details": {
                "tables_synced": tables_synced,
                "records_synced": records_synced,
                "tables_skipped": tables_skipped,
                "salesforce_objects_synced": salesforce_objects_synced,
            },
            "sync_type": sync_type,
        }
        return resp

    def normalize_fields(self, fields: list):
        normalize_mapper = {
            "currency": "string",
            "date": "datetime",
            "string": "string",
            "id": "uuid",
            "percent": "string",
            "reference": "foreign_reference",
            "textarea": "text",
            "double": "numeric",
            "datetime": "datetime",
            "picklist": "enum",
            "boolean": "boolean",
            "int": "int",
            "email": "string",
            "address": "string",
            "url": "string",
            "phone": "string",
        }
        try:
            [
                field.update({"field_type": normalize_mapper[field["field_type"]]})
                for field in fields
            ]
            return fields
        except Exception as e:
            return str(e)
