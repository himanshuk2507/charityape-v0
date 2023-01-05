import shortuuid


def orgGen():
    org_id = f"ORG-{shortuuid.uuid()}"
    return org_id


def cache_id_gen():
    cache_id = f"FB-{shortuuid.uuid()[:12]}"
    return cache_id


def getOrg(jwt_token):
    claims = jwt_token
    return claims["org"]
