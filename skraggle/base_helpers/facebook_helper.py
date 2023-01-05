from urllib.parse import urlencode

import requests

FACEBOOK_GRAPH_URL = "https://graph.facebook.com/"
FACEBOOK_WWW_URL = "https://www.facebook.com/"
FACEBOOK_OAUTH_DIALOG_PATH = "dialog/oauth?"


class FaceConnect:
    def __init__(
        self,
        app_id=None,
        app_secret=None,
        redirect_uri=None,
        short_access_token=None,
        short_page_token=None,
        long_access_token=None,
        long_page_token=None,
        version=12.0,
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.short_access_token = short_access_token
        self.short_page_token = short_page_token
        self.long_access_token = long_access_token
        self.long_page_token = long_page_token
        self.version = "v" + str(version)

    def get_client_auth_url(self, session_id=None, perms=None, **kwargs):
        """Build a URL to create an OAuth dialog."""
        url = "{0}{1}/{2}".format(
            FACEBOOK_WWW_URL, self.version, FACEBOOK_OAUTH_DIALOG_PATH
        )

        args = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "state": str(session_id),
        }
        if perms:
            args["scope"] = ",".join(perms)
        args.update(kwargs)
        return url + urlencode(args)

    def fetch_access_token(self, authorization_code):
        params = (
            ("client_id", self.app_id),
            ("redirect_uri", self.redirect_uri),
            ("client_secret", self.app_secret),
            ("code", authorization_code),
        )
        try:
            retrived_access_token_response = requests.get(
                f"https://graph.facebook.com/{self.version}/oauth/access_token",
                params=params,
            )
            if not retrived_access_token_response:
                return False, retrived_access_token_response.json().get("error")

            access_token = retrived_access_token_response.json().get("access_token")
            return True, access_token
        except Exception as e:
            return False, str(e)[:105]

    def extend_access_token(self, access_token):
        params = (
            ("client_id", self.app_id),
            ("client_secret", self.app_secret),
            ("fb_exchange_token", access_token),
            ("grant_type", "fb_exchange_token"),
        )
        try:
            retrived_access_token_response = requests.get(
                f"https://graph.facebook.com/{self.version}/oauth/access_token",
                params=params,
            )
            if not retrived_access_token_response:
                return False, retrived_access_token_response.json().get("error")
            extended_access_token = retrived_access_token_response.json().get(
                "access_token"
            )
            return True, extended_access_token
        except Exception as e:
            return False, str(e)[:105]

    def get_extended_page_tokens(self, long_access_token):
        fetch_page_AccessTokens_url = (
            f"https://graph.facebook.com/me/accounts?access_token={long_access_token}"
        )
        try:
            retrived_pages_response = requests.get(fetch_page_AccessTokens_url)
            if not retrived_pages_response:
                return False, retrived_pages_response.json().get("error")
            _page_access_tokens_obj = {
                x["name"]: {"page_id": x["id"], "page_access_token": x["access_token"]}
                for x in retrived_pages_response.json()["data"]
            }

            return True, _page_access_tokens_obj
        except Exception as e:
            return False, str(e)[:105]

    def fetch_info(self, access_token, object_id="me", fields="id,name"):
        params = (
            ("fields", fields),
            ("access_token", access_token),
        )

        response = requests.get(
            f"https://graph.facebook.com/v12.0/{object_id}", params=params
        )
        return response.json()
