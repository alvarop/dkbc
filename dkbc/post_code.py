import os
import requests
import time
import yaml

cfg = {}
if os.path.isfile("config.yml"):
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
else:
    print("config.yml not found!")
    cfg["client-id"] = input("Enter client id: ")
    cfg["client-secret"] = input("Enter client secret: ")

redirect_uri = "https://alvarop.com/dkbc/dk_oauth.html"


# https://api-portal.digikey.com/app_overview
url = "https://sso.digikey.com/as/authorization.oauth2?response_type=code&client_id={}&redirect_uri={}".format(
    cfg["client-id"], redirect_uri
)

print("Go to {} and get code from URL after logging in".format(url))

code = input("Enter code here:")

post_request = {
    "code": code,
    "client_id": cfg["client-id"],
    "client_secret": cfg["client-secret"],
    "redirect_uri": redirect_uri,
    "grant_type": "authorization_code",
}

# code  The authorization code returned from the initial request (See above example).
# client_id This is the client id assigned to the application that you generated within the API Portal.
# client_secret This is the client secret assigned to the application that you generated within the API Portal.
# redirect_uri  This URI must match the redirect URI that you defined while creating your application within the API Portal.
# grant_type    As defined in the OAuth 2.0 specification, this field must contain a value of authorization_code.

request_url = "https://sso.digikey.com/as/token.oauth2"

print("Making request to")
r = requests.post(request_url, data=post_request)
response = r.json()
print(response)

if r.status_code == 200:
    with open("old_config.yml", "w") as outfile:
        yaml.dump(cfg, outfile, default_flow_style=False)

    cfg["refresh-token"] = response["refresh_token"]
    cfg["access-token"] = response["access_token"]
    cfg["token-expiration"] = int(time.time()) + int(response["expires_in"])
    with open("config.yml", "w") as outfile:
        yaml.dump(cfg, outfile, default_flow_style=False)
else:
    print("ERROR")
