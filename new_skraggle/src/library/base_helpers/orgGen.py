from src.library.utility_classes.text_generator import TextGenerator


def orgGen():    
    org_id = f"ORG-{TextGenerator(length=12).random_string(selection=TextGenerator.password_level_string())}"
    return org_id

def getOrg(jwt_token):
    claims = jwt_token
    return claims["org"]
