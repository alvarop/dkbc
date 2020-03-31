#
# Script to getauthorization code from Digi-key by providing
# client-id and client-secret
# See https://developer.digikey.com/documentation/oauth for more info
#
import argparse
import os
import requests
import time
import webbrowser
import yaml


DEFAULT_REDIRECT_URI = "https://alvarop.com/dkbc/dk_oauth.html"
DEFAULT_API_URL = "https://api.digikey.com"


def authorize(config_path, api_url, redirect_uri):
    cfg = {}
    if os.path.isfile(config_path):
        with open(config_path, "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
    else:
        print('"{}" not found!'.format(config_path))
        cfg["client-id"] = input("Enter client id: ")
        cfg["client-secret"] = input("Enter client secret: ")

    url = (
        api_url
        + "/v1/oauth2/authorize?response_type=code&client_id={}&redirect_uri={}".format(
            cfg["client-id"], redirect_uri
        )
    )

    print("Go to {} and get code from URL after logging in".format(url))
    webbrowser.open(url)

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

    request_url = api_url + "/v1/oauth2/token"

    print("Making request to")
    r = requests.post(request_url, data=post_request)
    response = r.json()
    print(response)

    if r.status_code == 200:
        with open("old_config.yml", "w") as outfile:
            yaml.dump(cfg, outfile, default_flow_style=False)
        print(response)
        cfg["refresh-token"] = response["refresh_token"]
        cfg["access-token"] = response["access_token"]
        cfg["token-expiration"] = int(time.time()) + int(response["expires_in"])
        with open(config_path, "w") as outfile:
            yaml.dump(cfg, outfile, default_flow_style=False)
    else:
        print("ERROR")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--config_path", help="Configuration filename", default="config.yml"
    )
    parser.add_argument(
        "--api_url", help="Digi-key API url (sandbox or prod)", default=DEFAULT_API_URL
    )
    parser.add_argument(
        "--redirect_uri", help="OAuth Redirect URI", default=DEFAULT_REDIRECT_URI
    )
    args = parser.parse_args()

    authorize(
        config_path=args.config_path,
        api_url=args.api_url,
        redirect_uri=args.redirect_uri,
    )
