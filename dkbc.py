import http.client
import yaml
import json
import requests
import time


def refresh_token(cfg):
    # https://api-portal.digikey.com/app_overview

    post_request = {
        "refresh_token": cfg["refresh-token"],
        "client_id": cfg["client-id"],
        "client_secret": cfg["client-secret"],
        "grant_type": "refresh_token",
    }

    # code  The authorization code returned from the initial request (See above example).
    # client_id This is the client id assigned to the application that you generated within the API Portal.
    # client_secret This is the client secret assigned to the application that you generated within the API Portal.
    # redirect_uri  This URI must match the redirect URI that you defined while creating your application within the API Portal.
    # grant_type    As defined in the OAuth 2.0 specification, this field must contain a value of authorization_code.

    request_url = "https://sso.digikey.com/as/token.oauth2"

    print("Making request to")
    r = requests.post(request_url, data=post_request)
    print(r.status_code)
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

    return cfg


def dk_process_barcode(barcode):

    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    if int(cfg["token-expiration"]) < time.time():
        print("Token has expired, refreshing")
        cfg = refresh_token(cfg)

    conn = http.client.HTTPSConnection("api.digikey.com")

    payload = '{"QRCODE":"' + barcode + '"}'

    headers = {
        "x-ibm-client-id": cfg["client-id"],
        "authorization": cfg["access-token"],
        "content-type": "application/json",
        "accept": "application/json",
    }

    conn.request(
        "POST", "/services/barcode/v1/productqrcode", payload.encode("utf-8"), headers
    )

    res = conn.getresponse()
    data = json.loads(res.read())

    if "httpMessage" in data and data["httpMessage"] == "Unauthorized":
        print("Unauthorized! Need to refresh token.")

    return data


def dk_get_part_details(part_no):

    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    if int(cfg["token-expiration"]) < time.time():
        print("Token has expired, refreshing")
        cfg = refresh_token(cfg)

    conn = http.client.HTTPSConnection("api.digikey.com")

    # TODO - escape part_no quotes
    payload = (
        '{"Part": "'
        + part_no
        + '","IncludeAllAssociatedProducts": "false","IncludeAllForUseWithProducts": "false"}'
    )

    headers = {
        "x-ibm-client-id": cfg["client-id"],
        "authorization": cfg["access-token"],
        "content-type": "application/json",
        "accept": "application/json",
    }

    conn.request(
        "POST", "/services/partsearch/v2/partdetails", payload.encode("utf-8"), headers
    )

    res = conn.getresponse()
    data = json.loads(res.read())

    if "httpMessage" in data and data["httpMessage"] == "Unauthorized":
        print("Unauthorized! Need to refresh token.")

    return data
