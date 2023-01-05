import requests


BASE_URL = "https://api.neoncrm.com/neonws/services/api"


class NeonConnect:
    def __init__(
        self, api_key=None, org_id=None,
    ):
        self.API_KEY = api_key
        self.ORG_ID = org_id

    def getSession(self):
        url = f"{BASE_URL}/common/login?login.apiKey={self.API_KEY}&login.orgid={self.ORG_ID}"
        session_resp = requests.get(url)
        if session_resp.json()["loginResponse"]["operationResult"] == "FAIL":
            return False, session_resp.json()["loginResponse"]["errors"]['error'][0]['errorMessage']
        session_id = session_resp.json()["loginResponse"].get("userSessionId")
        return True, session_id
